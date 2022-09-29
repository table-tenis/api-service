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

""" Add new enterprise. """
# @enterprise_router.post("/")
# async def add_a_new_enterprise(enterprise: Enterprise,
#                                authorization: Authorization = Security(scopes=["root"]),
#                                session = Depends(get_session)) -> dict:
#     if enterprise.id != None:
#         enterprise_exist = db.get_by_id(session, select(Enterprise).where(Enterprise.id == enterprise.id))
#         if enterprise_exist:
#             raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Enterprise Supplied Id Is Existed."
#         )
#         enterprise_exist = db.get_by_id(session, select(Enterprise).where(Enterprise.enterprise_code == enterprise.enterprise_code))
#         if enterprise_exist:
#             raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Enterprise Supplied Enterprise_code Is Existed."
#         )
#     enterprise = db.add(session, enterprise)
#     return {
#         "Response": "New Enterprise Successfully Registered!",
#         "Enterprise_Id": enterprise.id
#     }

""" Get all enterprise info. Apply for root user. """
@enterprise_router.get("/")
async def get_enterprises(session = Depends(get_session)):
    statement = select(Enterprise)
    enterprises = db.get_all(session, statement)
    return enterprises[0][0]

""" Update enterprise info. Apply for root user """ 
@enterprise_router.put("/", response_model=Enterprise)
async def update_enterprise_info(body: EnterpriseBase,
                                session = Depends(get_session)):
    enterprises = db.get_all(session, select(Enterprise))
    enterprise = enterprises[0][0]
    if enterprise:
        enterprise_data = body.dict(exclude_unset=True)
        for key, value in enterprise_data.items():
            setattr(enterprise, key, value)
        enterprise = db.add(session, enterprise)
        return enterprise
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Enterprise Does Not Exist"
    )
    
""" Delete an enterprise. Apply for root user. """
# @enterprise_router.delete("/")
# async def delete_a_enterprise(id: int = Query(), 
#                                 authorization: Authorization = Security(scopes=["enterprise", "d"]),
#                                 session = Depends(get_session)):
#     enterprise = db.get_by_id(session, select(Enterprise).where(Enterprise.id == id))
#     if enterprise:
#         db.delete(session, enterprise)
#         return {
#             "Response": "Enterprise Deleted Successfully"
#         }      
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Enterprise Supplied Id Does Not Exist"
#     )