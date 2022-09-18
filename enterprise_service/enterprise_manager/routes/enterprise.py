from email import header
from random import seed
from time import time

from fastapi import APIRouter, HTTPException, Query, status, Depends, Security
from fastapi.routing import APIRoute
from typing import List
from sqlmodel import Session, select
from sqlalchemy.orm import load_only

from models import Enterprise, EnterpriseBase

from dependencies import CommonQueryParams, Authorization
from core.database import redis_db, get_session, engine, db

enterprise_router = APIRouter(tags=["Enterprise"])

class EnterpriseValid:
    def __init__(self, statement=None, id = None):
        self.statement = statement
        self.id = id

def verify_enterprise_authorization(key, enterprise_valid: EnterpriseValid):
    if "*" not in key:
        enterprise_access_ids = []
        for tag_qualifier in key:
            enterprise_access_ids.append(tag_qualifier[0])

        if enterprise_valid.id != None and enterprise_valid.id not in enterprise_access_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail = "Permission Denied"
            )
        if enterprise_valid.id == None and enterprise_valid.statement != None:
            enterprise_valid.statement = enterprise_valid.statement.where(Enterprise.id.in_(enterprise_access_ids))
    return enterprise_valid

""" Add new enterprise. """
@enterprise_router.post("/")
async def add_a_new_enterprise(enterprise: Enterprise,
                            #    authorization: Authorization = Security(scopes=["root"]),
                               session = Depends(get_session)) -> dict:
    if enterprise.id != None:
        enterprise_exist = db.get_by_id(session, select(Enterprise).where(Enterprise.id == enterprise.id))
        if enterprise_exist:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise Supplied Id Is Existed."
        )
        enterprise_exist = db.get_by_id(session, select(Enterprise).where(Enterprise.enterprise_code == enterprise.enterprise_code))
        if enterprise_exist:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise Supplied Enterprise_code Is Existed."
        )
    enterprise = db.add(session, enterprise)
    return {
        "Response": "New Enterprise Successfully Registered!",
        "Enterprise_Id": enterprise.id
    }

""" Get all enterprise info. Apply for root user. """
@enterprise_router.get("/")
async def get_enterprises(id: int = Query(default=None), 
                            enterprise_code: str = Query(default=None),
                            query_params: CommonQueryParams = Depends(), 
                            authorization: Authorization = Security(scopes=["enterprise", "r"]),
                            session = Depends(get_session)):
    statement = select(Enterprise)
    # Some Resouces Match, And Not Root Account.
    # Retrieve Resources Belong To This Account
    enterprise_valid = EnterpriseValid(statement=statement, id=id)
    enterprise_valid = verify_enterprise_authorization(key=authorization.key, enterprise_valid=enterprise_valid)
    statement = enterprise_valid.statement

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

    enterprises = db.get_all(session, statement)
    if not enterprises:
        return {"Response": "Not Found!"}
    return [enter[0] for enter in enterprises]

""" Update enterprise info. Apply for root user """ 
@enterprise_router.put("/", response_model=Enterprise)
async def update_enterprise_info(body: EnterpriseBase, 
                                id: int = Query(), 
                                authorization: Authorization = Security(scopes=["enterprise", "u"]),
                                session = Depends(get_session)):
    enterprise_valid = EnterpriseValid(id=id)
    enterprise_valid = verify_enterprise_authorization(key=authorization.key, enterprise_valid=enterprise_valid)

    enterprise = db.get_by_id(session, select(Enterprise).where(Enterprise.id == id))
    if enterprise:
        enterprise_data = body.dict(exclude_unset=True)
        for key, value in enterprise_data.items():
            setattr(enterprise, key, value)
        enterprise = db.add(session, enterprise)
        return enterprise
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Enterprise Supplied Id Does Not Exist"
    )
    
""" Delete an enterprise. Apply for root user. """
@enterprise_router.delete("/")
async def delete_a_enterprise(id: int = Query(), 
                                authorization: Authorization = Security(scopes=["enterprise", "d"]),
                                session = Depends(get_session)):
    enterprise_valid = EnterpriseValid(id=id)
    enterprise_valid = verify_enterprise_authorization(key=authorization.key, enterprise_valid=enterprise_valid)
    
    enterprise = db.get_by_id(session, select(Enterprise).where(Enterprise.id == id))
    if enterprise:
        db.delete(session, enterprise)
        return {
            "Response": "Enterprise Deleted Successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Enterprise Supplied Id Does Not Exist"
    )