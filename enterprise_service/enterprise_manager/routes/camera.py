from time import time
from fastapi import APIRouter, HTTPException, status, Depends, Response, Security, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy import false, not_
from sqlmodel import select, or_, and_, not_
from sqlalchemy.orm import load_only

from models import Camera, Site, CameraBase
from schemas import CameraUpdate
from core.database import get_session, db, get_cursor

from dependencies import CommonQueryParams, Authorization
from core.database import redis_db
from json import dumps
from core.camera_discovery import run_wsdiscovery, profiling_camera
from core.tag_qualifier_tree import Tree, verify_query_params, print_subtree, gender_query
camera_router = APIRouter( tags=["Camera"] )
CAMERA_DISCOVERY_LIST = []

def camera_labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'site.enterprise_id = '
    elif tree.key[0] == 1:
        tree.name = 'camera.site_id = '
    elif tree.key[0] == 2:
        tree.name = 'camera.id = '
    for child in tree.children:
        camera_labeling_tree(child)
        
def camera_tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    camera_labeling_tree(root)
    # print_subtree(root)
    return gender_query(root)

""" Add new cameras. """
@camera_router.post("/")
async def add_new_cameras(new_cameras: List[Camera],
                          authorization: Authorization = Security(scopes=['enterprise.site.camera', 'c']),
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
                                cursor = Depends(get_cursor)):
    # This Block Verify Query Params With Tag Qualifier Authorizarion Tree.
    # If Size Of Matched Trees List Is 0, Query Params List Don't Match Any Tag Qualifier Authorization.
    # Else, We Have Matched_Trees. And Decorate Staetment With Matched_Tree.
    matched_trees = verify_query_params([enterprise_id, site_id, id], authorization.key)
    if len(matched_trees) == 0:
        return []
    filter_id_param = camera_tree_to_query(matched_trees)
        
    limit_param, search_param, sort_param, ip_param, name_param, description_param = "", "", "", "", "", ""
    print('common_params.search = ', common_params.search)
    if common_params.limit != None and common_params.limit != "":
        limit_param += f"limit {common_params.limit}"
    if common_params.search != None:
        search_param += f"camera.name like '%{common_params.search}%'"
    if sorted != None:
        if sorted[0] == "+":
            sort_param += f"order by camera.{sorted[1:]}"
        else:
            sort_param += f"order by camera.{sorted[1:]} desc"
    if ip != None:
        ip_param += f"camera.ip = '{ip}'"
    if name != None:
        name_param += f"camera.name = '{name}'"
    if description != None:
        description_param += f"camera.description like '%{description}%'"
    condition_statement = ""
    conditions_list = [filter_id_param, name_param, ip_param, description_param, search_param]
    for condition in conditions_list:
        if condition != '':
            condition_statement += ' and ' + condition
    print(condition_statement)
    statement = f"select camera.id, camera.site_id, camera.ip, camera.name, "\
                    "camera.description, camera.rtsp_uri, camera.stream "\
                    "from camera, site "\
                    "where camera.site_id = site.id {} {} {};"\
                    .format(condition_statement, sort_param, limit_param)
    print("statement = ", statement)
    try:
        cursor.execute(statement)
        cameras = cursor.fetchall()
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = str(e)
            )
    list_camera = [{'id':camera[0], 'site_id':camera[1], 'ip':camera[2], 'name':camera[3], 
                    'description': camera[4], 'rtsp_uri':camera[5], 'stream':camera[6]} for camera in cameras]
    # print(list_camera)
    return JSONResponse(content=jsonable_encoder(list_camera))

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
                            authorization: Authorization = Security(scopes=['enterprise.site.camera', 'u']),
                            session = Depends(get_session)):
    camera = db.get_by_id(session, select(Camera).where(Camera.id == id))
    if camera:
        site = db.get_by_id(session, select(Site).where(Site.id == camera.site_id))
        matched_trees = verify_query_params([site.enterprise_id, camera.site_id, camera.id], authorization.key)
        if len(matched_trees) == 0:
            return {"Response" : "Permission Denied!"}
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
async def delete_a_camera(id: int = Query(), 
                          authorization: Authorization = Security(scopes=['enterprise.site.camera', 'd']),
                          session = Depends(get_session)):
    camera = db.get_by_id(session, select(Camera).where(Camera.id == id))
    if camera:
        site = db.get_by_id(session, select(Site).where(Site.id == camera.site_id))
        matched_trees = verify_query_params([site.enterprise_id, camera.site_id, camera.id], authorization.key)
        if len(matched_trees) == 0:
            return {"Response" : "Permission Denied!"}
        db.delete(session, camera)
        return {
            "Response": "Camera Deleted Successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Camera Supplied Id Does Not Exist"
    )