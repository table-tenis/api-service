from fastapi import APIRouter, HTTPException, Security, status, Depends, Query
from typing import List
from sqlmodel import select
from sqlalchemy.orm import load_only

from models import ACLBase, ACL
from schemas import ACLUpdate
from core.database import get_session, db
from dependencies import CommonQueryParams, Authorization
from sqlalchemy.exc import IntegrityError

acl_router = APIRouter( tags=["Access Control List"])
    
""" ********************** MANIPULATE ACL DATA. *********************** """
    
""" Add a new acl entity. """
@acl_router.post("/")
async def add_an_acl(new_acl: ACL, 
                    authorization: Authorization = Security(scopes=["root"]),
                    session = Depends(get_session)) -> dict:
    statement = select(ACL).where(ACL.username == new_acl.username)
    statement = statement.where(ACL.tag_type == new_acl.tag_type)
    statement = statement.where(ACL.tag_qualifier == new_acl.tag_qualifier)
    acl = db.get_all(session, statement)
    if acl:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ACL Record Is Existed, Please Remove Before Add Or Update Its Permissions"
        )
    new_acl = db.add(new_acl)
    return {
        "Response": "New ACL Successfully Registered!"
    }

""" Get all acl info. Apply for root user. """
@acl_router.get("/")
async def get_acls(id: int = Query(default=None),
                            username: str = Query(default=None),
                            common_params: CommonQueryParams = Depends(),
                            authorization: Authorization = Security(),
                            session = Depends(get_session)):
    statement = select(ACL)
    if username != None:
        if not authorization.is_root and username != authorization.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Username Does Not Match"
            )
        statement = statement.where(ACL.username == username)
    elif username == None and not authorization.is_root:
        # Just retrieve acl records for only this sign-in account
        statement = statement.where(ACL.username == authorization.username)
    if id != None:
        statement = statement.where(ACL.id == id)
    if common_params.search != None:
        statement = statement.filter(ACL.username.contains(common_params.search))
    if common_params.sort != None:
        if common_params.sort[0] == "-":
            statement = statement.order_by(ACL.username.desc())
        elif common_params.sort[0] == "+":
            statement = statement.order_by(ACL.username.asc())
    if common_params.limit != None and common_params.limit > 0:
        statement = statement.limit(common_params.limit)
    
    acls = db.get_all(session, statement)
    if not acls:
        return {"Response": "Not Found"}
    return [acl[0] for acl in acls]
    
""" Update acl info. Apply for root user """ 
@acl_router.put("/", response_model=ACL)
async def update_an_acl(body: ACLUpdate, id: int = Query(), 
                        authorization: Authorization = Security(scopes=["root"]),
                        session = Depends(get_session)):
    acl = db.get_by_id(session, select(ACL).where(ACL.id == id))
    if acl:
        acl_data = body.dict(exclude_unset=True)
        for key, value in acl_data.items():
            setattr(acl, key, value)
        
        acl = db.add(acl)
        return acl   
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="ACL Supplied Id Does Not Exist"
    )
    
""" Delete an ACL. Apply for root user. """
@acl_router.delete("/")
async def delete_an_acl(id: int = Query(), 
                        authorization: Authorization = Security(scopes=["root"]),
                        session = Depends(get_session)):
    acl = db.get_by_id(session, select(ACL).where(ACL.id == id))
    if acl:
        db.delete(acl)
        return {
            "Response": "ACL Deleted Successfully"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ACL Supplied Id Does Not Exist"
    )