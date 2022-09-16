from email import header
from random import seed
from time import time

from fastapi import APIRouter, HTTPException, status, Depends, Security, Query
from fastapi.routing import APIRoute
from typing import List
from sqlmodel import Session, select
from sqlalchemy.orm import load_only

from models import Site, SiteBase
from schemas import SiteUpdate
from dependencies import CommonQueryParams
from core.database import redis_db, get_session, engine
from auth.authenticate import authenticate, oauth2_scheme

site_router = APIRouter(tags=["Site"])

# session = get_session()
""" Add new site. """
@site_router.post("/")
async def add_a_new_site(site: Site, session = Depends(get_session)) -> dict:
    if site.id != None:
        enterprise_exist = session.get(Site, site.id)
        if enterprise_exist:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site with id exist."
        )
    session.add(site)
    session.commit()
    response = {
        "message": "New Site successfully registered!",
        "site_id": site.id
    }
    session.refresh(site)
    return response

""" Get site info by site name or side id. Apply for root user. """
@site_router.get("/")
async def get_site_by_fields(id: int = Query(default=None), name: str = Query(default=None),
                             common_params: CommonQueryParams = Depends(),
                          session = Depends(get_session)):
    statement = select(Site)
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
    sites = session.execute(statement).all()
    if not sites:
        return {"Response" : "Not Found!"}
    site_list = []
    for site in sites:
        site_list.append(site[0])
    return site_list

""" Get all site info, belong to an enterprise """
@site_router.get("/enterprises/{enterprise_id}")
async def get_site_enterprise(enterprise_id: int, query_params: CommonQueryParams = Depends(), session = Depends(get_session)):
    statement = select(Site).where(Site.enterprise_id == enterprise_id)
    if query_params.search != None:
        statement = statement.filter(Site.name.contains(query_params.search))
    if query_params.sort != None:
        if query_params.sort[0] == "-":
            statement = statement.order_by(Site.name.desc())
        elif query_params.sort[0] == "+":
            statement = statement.order_by(Site.name.asc())
    if query_params.limit != None and query_params.limit > 0:
        statement = statement.limit(query_params.limit)
    sites = session.execute(statement).all()
    if not sites:
        return {"Response": "Not Found!"}
    site_list = []
    for site in sites:
        site_list.append(site[0])
    return site_list

""" Update site info. Apply for root user """ 
@site_router.put("/{id}", response_model=Site)
async def update_site_info(id: int, body: SiteUpdate, 
                                      session = Depends(get_session)):
    site = session.get(Site, id)
    if site:
        site_data = body.dict(exclude_unset=True)
        for key, value in site_data.items():
            setattr(site, key, value)
            
        session.add(site)
        session.commit()
        session.refresh(site)
        return site
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Site with supplied id does not exist"
    )
    
""" Delete a site. Apply for root user. """
@site_router.delete("/{id}")
async def delete_a_site(id: int, session = Depends(get_session)):
    site = session.get(Site, id)
    if site:
        session.delete(site)
        session.commit()
        return {
            "message": "Site deleted successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Site does not exist"
    )