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
from dependencies import CommonQueryParams, Authorization
from core.database import redis_db, get_session, engine, db

site_router = APIRouter(tags=["Site"])
class SiteValid:
    def __init__(self, statement=None, enterprise_id = None, site_id = None):
        self.statement = statement
        self.enterprise_id = enterprise_id
        self.site_id = site_id

class TagQualifierGraph:
    def __init__(self, qualifier_list) -> None:
        self.qualifier_to_index = {} # This is node list
        self.index_to_qualifier = []
        self.adjacency_list = []
        self.qualifier_to_index['level_0:'] = 0
        self.index_to_qualifier.append(('level_0:',0))
        self.adjacency_list.append([]) # List index for level 0. Comprise all index of level 1
        
        self.global_index = 1
        for tag_qualifier in qualifier_list: 
            self.add_edges(tag_qualifier)
        # Add list of index for level 0
        for key, value in self.qualifier_to_index.items():
            if 'level_1' in key:
                self.adjacency_list[0].append(value)
        
        print(self.qualifier_to_index)
        print(self.index_to_qualifier)
        print(self.adjacency_list)
        print("size of node = ", self.global_index)
        self.find_qualifier_required()
        
    def add_node(self, level = 'level_0', qualifier=1):
        composite_level = level + ':' + str(qualifier)
        if self.qualifier_to_index.get(composite_level) == None:
            self.qualifier_to_index[composite_level] = self.global_index
            self.index_to_qualifier.append((composite_level, qualifier))
            self.adjacency_list.append([])
            self.global_index += 1
        return self.qualifier_to_index[composite_level]
    
    def add_edge(self, qualifier1, qualifier2):
        index1 = self.qualifier_to_index[qualifier1]
        index2 = self.qualifier_to_index[qualifier2]
        if index2 not in self.adjacency_list[index1]:
            self.adjacency_list[index1].append(index2)
        
    def add_edges(self, tag_qualifier):
        high_level = len(tag_qualifier)+1
        for i in range(1, high_level):
            self.add_node('level_' + str(i), tag_qualifier[i-1])
            
        for i in range(1, high_level-1):
            self.add_edge('level_' + str(i) + ':' + str(tag_qualifier[i-1]), 'level_' + str(i+1) + ':' + str(tag_qualifier[i]))
     
    def find_all_qualifier(self, search_list):
        level_1_indexes = self.qualifier_to_index[search_list[0]]
        level_indexes_list = []
        for i in range(1, len(search_list)):
            # level_to_search = search_list[i-1]
            level_indexes = self.qualifier_to_index[search_list[i-1]]
            child_nodes = [self.index_to_qualifier[i] for i in level_indexes]
            pass
        
        for search_level in search_list:
            if self.qualifier_to_index.get(search_level) or '*' == search_level:
                pass       
     
    def find_qualifier_required(self, qualifier_required = [None, None, None]):
        search_list = [None for i in range(len(qualifier_required)+1)]
        search_list[0] = 'level_0:'
        for i in range(len(search_list)):
            if not search_list[i]:
                search_list[i] = '*'
        print(search_list)
        self.find_all_qualifier(search_list)
            
    
def verify_site_authorization(key, site_valid: SiteValid, session=None):
    tag_qualifier_graph = TagQualifierGraph(key)
    if "*" not in key:
        enterprise_access_ids = []
        site_access_ids = []
        matched = False
        for tag_qualifier in key:
            enterprise_access_ids.append(tag_qualifier[0])
            site_access_ids.append(tag_qualifier[1])
        if site_valid.enterprise_id == None and site_valid.site_id == None:
            print("Case 1: enterprise_access_ids = ", enterprise_access_ids)
            print("Case 1: site_access_ids = ", site_access_ids)
            if site_valid.statement != None:
                site_valid.statement = site_valid.statement.where(Site.enterprise_id.in_(enterprise_access_ids))
                site_valid.statement = site_valid.statement.where(Site.id.in_(site_access_ids))
        elif site_valid.enterprise_id != None and site_valid.site_id == None:
            print("Case 2: enterprise_access_ids = ", enterprise_access_ids)
            print("Case 2: site_access_ids = ", site_access_ids)
            if site_valid.enterprise_id in enterprise_access_ids:
                if site_valid.statement != None:
                    site_valid.statement = site_valid.statement.where(Site.enterprise_id == site_valid.enterprise_id)
                site_id_with_enter = []
                for i in range(len(enterprise_access_ids)):
                    if site_valid.enterprise_id == enterprise_access_ids[i]:
                        site_id_with_enter.append(site_access_ids[i])
                print("Case 2: site_id_with_enter = ", site_id_with_enter)
                if -1 not in site_id_with_enter:
                    if site_valid.statement != None:
                        site_valid.statement = site_valid.statement.where(Site.id.in_(site_id_with_enter))
            else:
                if -1 not in enterprise_access_ids:
                    raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail = "Permission Denied"
                )
        elif site_valid.enterprise_id == None and site_valid.site_id != None:
            print("Case 3: enterprise_access_ids = ", enterprise_access_ids)
            print("Case 3: site_access_ids = ", site_access_ids)
            if site_valid.site_id in site_access_ids:
                site = db.get_by_id(session, select(Site).where(Site.id == site_valid.site_id))
                if site.enterprise_id != enterprise_access_ids[site_access_ids.index(site_valid.site_id)]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail = "Permission Denied"
                    )
                if site_valid.statement != None:
                        site_valid.statement = site_valid.statement.where(Site.id == site_valid.site_id)
            else:
                if -1 not in site_access_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail = "Permission Denied"
                    )
        else:
            print("Case 4: enterprise_access_ids = ", enterprise_access_ids)
            print("Case 4: site_access_ids = ", site_access_ids)
            site_id_with_enter = []
            for i in range(len(enterprise_access_ids)):
                if site_valid.enterprise_id == enterprise_access_ids[i]:
                    site_id_with_enter.append(site_access_ids[i])
            print("Case 4: site_id_with_enter = ", site_id_with_enter)
            if len(site_id_with_enter) == 0:
                raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail = "Permission Denied"
                    )
            if site_valid.site_id in site_id_with_enter or -1 in site_id_with_enter:
                if site_valid.statement != None:
                    site_valid.statement = site_valid.statement.where(Site.id == site_valid.site_id)
    return site_valid

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
                            name: str = Query(default=None),
                            common_params: CommonQueryParams = Depends(),
                            authorization: Authorization = Security(scopes=['enterprise.site.camera', 'r']),
                            session = Depends(get_session)):
    
    tag_qualifier_graph = TagQualifierGraph(authorization.key)
    statement = select(Site)
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