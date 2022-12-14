from time import time

from fastapi import APIRouter, HTTPException, status, Depends, Security, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel import Session, select, and_, or_, not_
from sqlalchemy.orm import load_only

from models import Site, SiteBase
from schemas import SiteUpdate
from dependencies import CommonQueryParams, Authorization
from core.database import get_session, engine, db, get_cursor
from core.tag_qualifier_tree import Tree, verify_query_params, print_subtree, gender_query
site_router = APIRouter(tags=["Site"])

# Labeling to tree nodes for assign condition query
def site_labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'site.id = '
    for child in tree.children:
        site_labeling_tree(child)

# Site trees to condition query        
def site_tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    site_labeling_tree(root)
    # print_subtree(root)
    return gender_query(root)           

""" Add new site. """
@site_router.post("/")
async def add_a_new_site(site: Site, 
                         authorization: Authorization = Security(scopes=['site', 'c']),
                         session = Depends(get_session)) -> dict:
    if site.id != None:
        site_exist = db.get_by_id(session, select(Site).where(Site.id == site.id))
        if site_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site Supplied Id Is Existed."
            )
    site = db.add(session, site)
    return {
        "Response": "New Site Successfully Registered!",
        "Id": site.id
    }

""" Get site info by site name or side id. Apply for root user. """
@site_router.get("/")
async def get_sites(id: int = Query(default=None), 
                    name: str = Query(default=None),
                    search: str = Query(default=None, regex="(name|description|note)-"),
                    sorted: str = Query(default=None, regex="^[+-](id|name)"),
                    limit: int = Query(default=None, gt=0),
                    authorization: Authorization = Security(scopes=['site', 'r']),
                    cursor = Depends(get_cursor)):
    # This Block Verify Query Params With Tag Qualifier Authorizarion Tree.
    # If Size Of Matched Trees List Is 0, Query Params List Don't Match Any Tag Qualifier Authorization.
    # Else, We Have Matched_Trees. And Decorate Staetment With Matched_Tree.
    matched_trees = verify_query_params([id], authorization.key)
    if len(matched_trees) == 0:
        return []
    filter_id_param = site_tree_to_query(matched_trees)
        
    limit_param, search_param, sort_param, name_param = "", "", "", ""
    
    # Add limit query
    if limit != None and limit != "":
        limit_param += f"limit {limit}"
    # Add search query
    if search != None:
        search = search.split('-')
        if search[1] != '':
            search_param += f"site.{search[0]} like '%{search[1]}%'"
    # Add order by query
    if sorted != None:
        if sorted[0] == "+":
            sort_param += f"order by site.{sorted[1:]}"
        else:
            sort_param += f"order by site.{sorted[1:]} desc"
    if name != None:
        name_param += f"site.name = '{name + ''}'"
    
    # Complete condition statement
    condition_statement = ""
    conditions_list = [filter_id_param, name_param, search_param]
    first_add = False
    for condition in conditions_list:
        if condition != '':
            if not first_add:
                condition_statement = 'where ' + condition
                first_add = True
            else:
                condition_statement += ' and ' + condition
    print(condition_statement)
    statement = f"select site.id, site.name, site.description, site.note "\
                    "from site "\
                    "{} {} {};"\
                    .format(condition_statement, sort_param, limit_param)
    print("statement = ", statement)
    try:
        cursor.execute(statement)
        sites = cursor.fetchall()
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = str(e)
            )
    list_site = [{'id':site[0], 'name':site[1], 
                  'description':site[2], 'note': site[3]} for site in sites]
    # print(list_camera)
    return JSONResponse(content=jsonable_encoder(list_site))

""" Update site info. Apply for root user """ 
@site_router.put("/")
async def update_site_info(body: SiteBase, 
                            id: int = Query(), 
                            authorization: Authorization = Security(scopes=['site', 'u']),
                            session = Depends(get_session)):
    site = db.get_by_id(session, select(Site).where(Site.id == id))
    if site:
        matched_trees = verify_query_params([id], authorization.key)
        if len(matched_trees) == 0:
            return {"Response" : "Permission Denied!"}
        
        site_data = body.dict(exclude_unset=True)
        for key, value in site_data.items():
            setattr(site, key, value)

        site = db.add(session, site)
        return site
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Site Supplied Id Does Not Exist"
    )
    
""" Delete a site. Apply for root user. """
@site_router.delete("/")
async def delete_a_site(id: int = Query(), 
                        authorization: Authorization = Security(scopes=['site', 'd']),
                        session = Depends(get_session)):
    site = db.get_by_id(session, select(Site).where(Site.id == id))
    if site:
        matched_trees = verify_query_params([id], authorization.key)
        if len(matched_trees) == 0:
            return {"Response" : "Permission Denied!"}
        db.delete(session, site)
        return {
            "Response": "Site Deleted Successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Site Does Not Exist"
    )