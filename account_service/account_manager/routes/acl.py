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
    if len(new_acl.tag_type.split('.')) != len(new_acl.tag_qualifier.split('.')):
        raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Can't Insert This ACL, Len Tag_Type And Tag_Qualifier Not Match"
                    )
    statement = select(ACL).where(ACL.username == new_acl.username)
    statement = statement.where(ACL.tag_type == new_acl.tag_type)
    acls = db.get_all(session, statement)
    if acls:
        insert_tag_qualifier = new_acl.tag_qualifier
        insert_tag_qualifier = insert_tag_qualifier.split('.')
        for acl in acls:
            exist_tag_qualifier = acl[0].tag_qualifier
            exist_tag_qualifier = exist_tag_qualifier.split('.')
            length = min(len(insert_tag_qualifier), len(exist_tag_qualifier))
            for i in range(length):
                if exist_tag_qualifier[i] == '-1' and insert_tag_qualifier[i] != '-1':
                    if '.'.join(exist_tag_qualifier[:i]) == '.'.join(insert_tag_qualifier[:i]):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Can't Insert This ACL, Tag_Qualifier Overlapping"
                        )
                elif insert_tag_qualifier[i] == '-1' and exist_tag_qualifier[i] != '-1':
                    if '.'.join(exist_tag_qualifier[:i]) == '.'.join(insert_tag_qualifier[:i]):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Can't Insert This ACL, Tag_Qualifier Overlapping"
                        )
            
    statement = statement.where(ACL.tag_qualifier == new_acl.tag_qualifier)
    acls = db.get_all(session, statement)
    if acls:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ACL Record Is Existed, Please Remove Before Add Or Update Its Permissions"
        )
    new_acl = db.add(session, new_acl)
    return {
        "Response": "New ACL Successfully Registered!"
    }

""" Get all acl info. Apply for root user. """
@acl_router.get("/")
async def get_acls(id: int = Query(default=None),
                    username: str = Query(default=None),
                    sorted: str = Query(default=None, regex="^[+-](id|username|tag_type)"),
                    search: str = Query(default=None, regex="(username)-"),
                    limit: int = Query(default=None, gt=0),
                    authorization: Authorization = Security(),
                    session = Depends(get_session)):
    statement = select(ACL)
    if username != None:
        if not authorization.is_root and username != authorization.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission Denied!"
            )
        statement = statement.where(ACL.username == username)
    elif username == None and not authorization.is_root:
        # Just retrieve acl records for only this sign-in account
        statement = statement.where(ACL.username == authorization.username)
    if id != None:
        statement = statement.where(ACL.id == id)
    if search != None:
        search = search.split('-')
        if search[1] != '':
            statement = statement.filter(ACL.username.contains(search[1]))
    if sorted != None:
        if sorted[0] == "-":
            if sorted[1:] == 'id':
                statement = statement.order_by(ACL.id.desc())
            elif sorted[1:] == 'username':
                statement = statement.order_by(ACL.username.desc())
            elif sorted[1:] == 'tag_type':
                statement = statement.order_by(ACL.tag_type.desc())
        elif sorted[0] == "+":
            if sorted[1:] == 'id':
                statement = statement.order_by(ACL.id.asc())
            elif sorted[1:] == 'username':
                statement = statement.order_by(ACL.username.asc())
            elif sorted[1:] == 'tag_type':
                statement = statement.order_by(ACL.tag_type.asc())
    if limit != None and limit > 0:
        statement = statement.limit(limit)
    
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
        
        acl = db.add(session, acl)
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
        db.delete(session, acl)
        return {
            "Response": "ACL Deleted Successfully"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ACL Supplied Id Does Not Exist"
    )