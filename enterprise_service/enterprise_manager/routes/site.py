from email import header
from random import seed
from time import time

from fastapi import APIRouter, HTTPException, status, Depends, Security, Query
from fastapi.routing import APIRoute
from typing import List
from sqlmodel import Session, select, and_, or_, not_
from sqlalchemy.orm import load_only

from models import Site, SiteBase
from schemas import SiteUpdate
from dependencies import CommonQueryParams, Authorization
from core.database import redis_db, get_session, engine, db
from core.tag_qualifier_tree import verify_query_params, print_subtree
site_router = APIRouter(tags=["Site"])
class SiteValid:
    def __init__(self, statement=None, enterprise_id = None, site_id = None):
        self.statement = statement
        self.enterprise_id = enterprise_id
        self.site_id = site_id
      
def add_condition_by_tree(tree):
    and_condition = []
    print('tree_key[1] = ', tree.key[1])
    if -1 != tree.key[1]:
        and_condition.append(Site.enterprise_id == tree.key[1])
        site_id = []
        for subtree in tree.children:
            site_id.append(subtree.key[1])
        if -1 not in site_id:
            and_condition.append(Site.id.in_(site_id))
            
    if len(and_condition) > 0:
        print('and_condition = ', and_condition, and_(*and_condition))
        return and_condition
    return None
          
def add_site_subtree_query(subtree_query, statement):
    or_conditions = []
    if len(subtree_query) > 0:
        for tree in subtree_query:
            sub_and_condition = add_condition_by_tree(tree)
            print(sub_and_condition)
            if sub_and_condition :
                or_conditions.append(and_(*sub_and_condition))
    if len(or_conditions) > 0:
        statement = statement.where(*or_conditions)
        print('statement = ', statement)
        
    
        # statement = statement.where(and_(Site.enterprise_id.in_(enterprise_ids)))               

""" Add new site. """
@site_router.post("/")
async def add_a_new_site(site: Site, session = Depends(get_session)) -> dict:
    if site.id != None:
        enterprise_exist = db.get_by_id(session, select(Site).where(Site.id == site.id))
        if enterprise_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site Supplied Id Is Existed."
            )
    enterprise_exist = db.get_by_id(session, select(Site).where(Site.name == site.name).where(Site.enterprise_id == site.enterprise_id))
    if enterprise_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site Supplied Name And Enterprise Id Is Existed."
        )
    site = db.add(session, site)
    return {
        "Response": "New Site Successfully Registered!",
        "Site_Id": site.id
    }

""" Get site info by site name or side id. Apply for root user. """
@site_router.get("/")
async def get_site_by_fields(enterprise_id: int = Query(default=None),
                            id: int = Query(default=None),
                            cam_id: int = Query(default=None), 
                            name: str = Query(default=None),
                            common_params: CommonQueryParams = Depends(),
                            authorization: Authorization = Security(scopes=['enterprise.site', 'r']),
                            session = Depends(get_session)):
    statement = select(Site)
    subtree_query = verify_query_params([enterprise_id, id], authorization.key)
    for tree in subtree_query:
        print('-------------')
        print_subtree(tree)
    add_site_subtree_query(subtree_query, statement)
    if enterprise_id != None:
        statement = statement.where(Site.enterprise_id == enterprise_id)
    if id != None:
        statement = statement.where(Site.id == id)
    if name != None:
        statement = statement.where(Site.name == name)
    if common_params.search != None:
        statement = statement.filter(Site.name.contains(common_params.search))
    if common_params.sort != None:
        if common_params.sort[0] == "-":
            statement = statement.order_by(Site.name.desc())
        elif common_params.sort[0] == "+":
            statement = statement.order_by(Site.name.asc())
    if common_params.limit != None and common_params.limit > 0:
        statement = statement.limit(common_params.limit)
    # print('statement = ', str(statement))
    sites = db.get_all(session, statement)
    if not sites:
        return {"Response" : "Not Found!"}
    return [site[0] for site in sites]

""" Update site info. Apply for root user """ 
@site_router.put("/", response_model=Site)
async def update_site_info(body: SiteUpdate, 
                            id: int = Query(), 
                            session = Depends(get_session)):
    site = db.get_by_id(session, select(Site).where(Site.id == id))
    if site:
        site_data = body.dict(exclude_unset=True)
        for key, value in site_data.items():
            setattr(site, key, value)
            
        try:
            site = db.add(session, site)
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = e._message()
        )
        return site
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Site Supplied Id Does Not Exist"
    )
    
""" Delete a site. Apply for root user. """
@site_router.delete("/")
async def delete_a_site(id: int = Query(), session = Depends(get_session)):
    site = db.get_by_id(session, select(Site).where(Site.id == id))
    if site:
        db.delete(session, site)
        return {
            "Response": "Site Deleted Successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Site Does Not Exist"
    )