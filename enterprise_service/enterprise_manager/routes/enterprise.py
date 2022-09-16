from email import header
from random import seed
from time import time

from fastapi import APIRouter, HTTPException, Query, status, Depends, Security
from fastapi.routing import APIRoute
from typing import List
from sqlmodel import Session, select
from sqlalchemy.orm import load_only

from models import Enterprise, EnterpriseBase

from dependencies import CommonQueryParams
from core.database import redis_db, get_session, engine
from auth.authenticate import authenticate, oauth2_scheme

enterprise_router = APIRouter(tags=["Enterprise"])

# session = get_session()
""" Add new enterprise. """
@enterprise_router.post("/")
async def add_a_new_enterprise(enterprise: Enterprise, session = Depends(get_session)) -> dict:
    if enterprise.id != None:
        enterprise_exist = session.get(Enterprise, enterprise.id)
        if enterprise_exist:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise with id exist."
        )
        enterprise_exist = session.get(Enterprise, enterprise.enterprise_code)
        if enterprise_exist:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise with enterprise_code exist."
        )
    session.add(enterprise)
    session.commit()
    response = {
        "message": "New Enterprise successfully registered!",
        "enterprise_id": enterprise.id
    }
    session.refresh(enterprise)
    return response

""" Get all enterprise info. Apply for root user. """
@enterprise_router.get("/")
async def get_enterprises(id: int = Query(default=None), enterprise_code: str = Query(default=None),
                          query_params: CommonQueryParams = Depends(), session = Depends(get_session)):
    statement = select(Enterprise)
    if id != None:
        statement = statement.where(Enterprise.id == id)
    if enterprise_code != None:
        statement = statement.where(Enterprise.enterprise_code == enterprise_code)
    if query_params.search != None:
        statement = statement.filter(Enterprise.enterprise_code.contains(query_params.search))
    if query_params.sort != None:
        if query_params.sort[0] == "-":
            statement = statement.order_by(Enterprise.enterprise_code.desc())
        elif query_params.sort[0] == "+":
            statement = statement.order_by(Enterprise.enterprise_code.asc())
    if query_params.limit != None and query_params.limit > 0:
        statement = statement.limit(query_params.limit)
    enterprises = session.execute(statement).all()
    if not enterprises:
        return {"Response": "Not Found!"}
    enter_list = []
    for enter in enterprises:
        enter_list.append(enter[0])
    return enter_list

""" Update enterprise info. Apply for root user """ 
@enterprise_router.put("/{id}", response_model=Enterprise)
async def update_enterprise_info(id: int, body: EnterpriseBase, 
                                      session = Depends(get_session)):
    enterprise = session.get(Enterprise, id)
    if enterprise:
        enterprise_data = body.dict(exclude_unset=True)
        for key, value in enterprise_data.items():
            setattr(enterprise, key, value)
            
        session.add(enterprise)
        session.commit()
        session.refresh(enterprise)
        return enterprise
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Enterprise with supplied id does not exist"
    )
    
""" Delete a enterprise. Apply for root user. """
@enterprise_router.delete("/{id}")
async def delete_a_enterprise(id: int, session = Depends(get_session)):
    enterprise = session.get(Enterprise, id)
    if enterprise:
        session.delete(enterprise)
        session.commit()
        return {
            "message": "Enterprise deleted successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Enterprise does not exist"
    )