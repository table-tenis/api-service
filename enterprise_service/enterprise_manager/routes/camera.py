from importlib.metadata import entry_points
from time import time
from fastapi import APIRouter, HTTPException, status, Depends, Response, Security, Query
from typing import List
from sqlalchemy import not_
from sqlmodel import select, or_, and_, not_
from sqlalchemy.orm import load_only

from models import Camera, Site, CameraBase
from schemas import CameraUpdate
from core.database import get_session, db

from dependencies import CommonQueryParams, Authorization
from core.database import redis_db
import json
from core.camera_discovery import run_wsdiscovery, profiling_camera
from core.tag_qualifier_tree import Tree, verify_query_params, print_subtree
camera_router = APIRouter( tags=["Camera"] )
CAMERA_DISCOVERY_LIST = []


def gender_query(tree):
    if tree.key[1] == -1 and tree.key[0] != -1:
        return ""
    
    id = ""
    if tree.key[1] != -1:
        id = str(tree.key[1])

    sub_id = ""
    for child in tree.children:
        if sub_id == "":
            sub_id += gender_query(child)
        else:
            sub_id += " or " + gender_query(child)
        
    if sub_id != "":
        if id == "":
            id = sub_id
        else:
            id  = id + " and ( " + sub_id + " )"
        
    return id

def labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'enterprise'
    elif tree.key[0] == 1:
        tree.name = 'site'
    elif tree.key[0] == 2:
        tree.name = 'camera'
    for child in tree.children:
        labeling_tree(child)
        
def tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    labeling_tree(root)
    print_subtree(root)
    return gender_query(root)
    
# Add And Condition For Each Matched Tree.     
def add_and_condition_in_tree(session, tree):
    and_condition = []
    print('tree_key = ', tree.key[1])
    site_id = []
    if -1 != tree.key[1]:    
        sites = db.get_all(session, select(Site).options(load_only("id")).where(Site.enterprise_id ==  tree.key[1]))
        sites_id = []
        for site in sites:
            sites_id.append(site[0].id)
        and_condition.append(Camera.site_id.in_(sites_id))
    for subtree in tree.children:
        site_id.append(subtree.key[1])
    print('site_id = ', site_id)
    if -1 not in site_id:
        and_condition.append(Camera.site_id.in_(site_id))
            
    if len(and_condition) > 0:
        print('and_condition = ', and_condition, and_(*and_condition))
        return and_condition
    return None
  
# Decorate Query Statement With Matched Trees.        
def decor_camera_statement(query_tree, session, statement):
    # Try To Reduce Query Tree To High = 2. Because Contrains In A Table Is Usually 2 Level.
    if -1 == query_tree[0].key[1]:
        # Root Of This Tree Have Qualifier Id = -1.
        # So Romove This Root, Decrease Tree 1 Level.
        query_tree = query_tree[0].children
    else:
        sub_tree = []
        for tree in query_tree:
            sites = db.get_all(session, select(Site).options(load_only("id")).where(Site.enterprise_id ==  tree.key[1]))
            sites_id = []
            for site in sites:
                sites_id.append(site[0].id)
            children = tree.children[:]
            for child in children:
                if child.key[1] != -1 and child.key[1] not in sites_id:
                    # Remove This Site Tree From Origin Tree
                    tree.children.remove(child)
                
    or_conditions = []
    if len(query_tree) > 0:
        for tree in query_tree:
            sub_and_condition = add_and_condition_in_tree(tree)
            print(sub_and_condition)
            if sub_and_condition :
                or_conditions.append(and_(*sub_and_condition))
    if len(or_conditions) > 0:
        # Add Or Condition For Entire Matched Trees.  
        statement = statement.where(or_(*or_conditions))
        print('tree statement = ', statement)    
    return statement  

""" Add new cameras. """
@camera_router.post("/")
async def add_new_cameras(new_cameras: List[Camera],
                            session = Depends(get_session)) -> dict:
    for new_camera in new_cameras:
        cameras = db.get_all(session, select(Camera).where(Camera.ip == new_camera.ip))
        if cameras:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ip Supplied Is Existed"
            )

    new_cameras = [dict(camera) for camera in new_cameras]
    # Insert a bulk of data using Core
    try:
        session.execute(
            Camera.__table__.insert(),
            new_cameras
        )
        session.commit()
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = e._message()
            )
    return {
            "Response": "New Privilege Successfully Registered!"
        }
    
""" Get site info by site name or side id. Apply for root user. """
@camera_router.get("/")
async def get_camera_by_fields(enterprise_id: int = Query(default=None),
                                site_id: int = Query(default=None),
                                id: int = Query(default=None), name: str = Query(default=None),
                                ip: str = Query(default=None), description: str = Query(default=None),
                                sorted: str = Query(default=None, regex="^[+-](id|site_id|ip|name)"),
                                common_params: CommonQueryParams = Depends(),
                                authorization: Authorization = Security(scopes=['enterprise.site.camera', 'r']),
                                session = Depends(get_session)):
    statement = select(Camera)
    # This Block Verify Query Params With Tag Qualifier Authorizarion Tree.
    # If Size Of Matched Trees List Is 0, Query Params List Don't Match Any Tag Qualifier Authorization.
    # Else, We Have Matched_Trees. And Decorate Staetment With Matched_Tree.
    matched_trees = verify_query_params([enterprise_id, site_id, id], authorization.key)
    if len(matched_trees) == 0:
        return {"Response" : "Not Found"}
    for tree in matched_trees:
        print('-------------')
        print_subtree(tree)
    print(tree_to_query(matched_trees))
    # statement = decor_site_statement(matched_trees, statement)
    
    if enterprise_id != None:
        sites = db.get_all(session, select(Site).options(load_only("id")).where(Site.enterprise_id == enterprise_id))
        sites_id = []
        for site in sites:
            sites_id.append(site[0].id)
        statement = statement.where(Camera.site_id.in_(sites_id))
    if site_id != None:
        statement = statement.where(Camera.site_id == site_id)
    if id != None:
        statement = statement.where(Camera.id == id)
    if name != None:
        statement = statement.where(Camera.name == name)
    if ip != None:
        statement = statement.where(Camera.ip == ip)
    if description != None:
        statement = statement.filter(Camera.description.contains(description))
    if common_params.search != None:
        statement = statement.filter(Camera.name.contains(common_params.search))
    if sorted != None:
        if sorted[0] == "-":
            if sorted[1:] == 'id':
                statement = statement.order_by(Camera.id.desc())
            elif sorted[1:] == 'site_id':
                statement = statement.order_by(Camera.site_id.desc())
            elif sorted[1:] == 'ip':
                statement = statement.order_by(Camera.ip.desc())
            elif sorted[1:] == 'name':
                statement = statement.order_by(Camera.name.desc())
        elif sorted[0] == "+":
            if sorted[1:] == 'id':
                statement = statement.order_by(Camera.id.asc())
            elif sorted[1:] == 'site_id':
                statement = statement.order_by(Camera.site_id.asc())
            elif sorted[1:] == 'ip':
                statement = statement.order_by(Camera.ip.asc())
            elif sorted[1:] == 'name':
                statement = statement.order_by(Camera.name.asc())
        
    if common_params.limit != None and common_params.limit > 0:
        statement = statement.limit(common_params.limit)

    cameras = db.get_all(session, statement)
    if not cameras:
        return {"Response" : "Not Found!"}
    return [camera[0] for camera in cameras]

""" Get an camera onvif profile by ip address. """
@camera_router.get("/profiles")
async def get_camera_profile(ip: str = Query(),
                        session = Depends(get_session)):
    profile = await profiling_camera(ip)
    return profile

""" Local Network Camera Discovery. """
@camera_router.get("/discovery/local")
async def discovery_camera_local_network(session = Depends(get_session)):
    ip_addrs = await run_wsdiscovery("239.255.255.250")
    ips_exist = []
    for ip in ip_addrs:
        cameras = db.get_all(session, select(Camera).where(Camera.ip == ip))
        if cameras:
            ips_exist.append(ip)
            
    for ip_exist in ips_exist:
        ip_addrs.remove(ip_exist)
    return ip_addrs

""" Outside Network Camera Discovery by ip address. """
@camera_router.get("/discovery/reliable")
async def discovery_camera_external_network_reliable(ip:str = Query(), session = Depends(get_session)):
    ip_addr = await run_wsdiscovery(ip)
    cameras = db.get_all(session, select(Camera).where(Camera.ip == ip))
    if (len(ip_addr) == 0) and cameras:
        res = ip + " Is Existed In Database, But Can Not Discovery"
        return {"Response": res}
    elif (len(ip_addr) == 1) and cameras:
        res = ip + " Is Exist In Database, And Can Discovery"
        return {"Response": res}
    else:
        return ip_addr
    
""" Outside Network Camera Discovery by ip address. """
@camera_router.get("/discovery/unreliable")
async def discovery_camera_external_network_unreliable(ip:str = Query(), session = Depends(get_session)):
    cameras = db.get_all(session, select(Camera).where(Camera.ip == ip))
    if cameras:
        res = ip + " Is Exist In Database, Does Not Discovery"
        return {"Response": res}
    ip_addr = await run_wsdiscovery(ip)
    return ip_addr

""" Update a camera info. """ 
@camera_router.put("/", response_model=Camera)
async def update_camera_info(body: CameraUpdate, 
                            id: int = Query(), 
                            session = Depends(get_session)):
    camera = db.get_by_id(session, select(Camera).where(Camera.id == id))
    if camera:
        camera_data = body.dict(exclude_unset=True)
        for key, value in camera_data.items():
            setattr(camera, key, value)
        camera = db.add(session, camera)  
        return camera
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Camera Supplied Id Does Not Exist"
    )
    
""" Delete a camera. Apply for root user. """
@camera_router.delete("/")
async def delete_a_camera(id: int = Query(), session = Depends(get_session)):
    camera = db.get_by_id(session, select(Camera).where(Camera.id == id))
    if camera:
        db.delete(session, camera)
        return {
            "Response": "Camera Deleted Successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Camera Supplied Id Does Not Exist"
    )