from fastapi import APIRouter, HTTPException, Security, status, Depends
from typing import List
from sqlmodel import select
from sqlalchemy.orm import load_only
from sqlalchemy.exc import IntegrityError

from models import Privileges, PrivilegeUpdate, Account_Privileges
from core.database import get_session
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from auth.authenticate import authenticate
from dependencies import CommonQueryParams, Permission

admin_router = APIRouter( tags=["Admin"])
hash_password = HashPassword()
    
""" ********************** MANIPULATE PRIVILEGES DATA. *********************** """
    
""" Add a new privilege. """
@admin_router.post("/privilege")
async def add_a_privilege(new_privilege: Privileges, 
                            permission: Permission = Security(scopes=["admin"])) -> dict:
    privilege = permission.session.execute(select(Privileges).where(Privileges.privilege_name == new_privilege.privilege_name)).first()
    if privilege:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Privilege with supplied name exists"
        )
    permission.session.add(new_privilege)
    permission.session.commit()
    permission.session.refresh(new_privilege)
    return {
        "message": "New Privilege successfully registered!"
    }

""" Add a list of privileges. """
@admin_router.post("/privileges")
async def add_a_list_privileges(new_privileges: List[Privileges], 
                                permission: Permission = Security(scopes=["admin"])) -> dict:
    for new_privilege in new_privileges:
        privilege = permission.session.execute(select(Privileges).where(Privileges.privilege_name == new_privilege.privilege_name)).first()
        if privilege:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Have Privileges with supplied name exists"
            )

    new_privileges = [dict(privilege) for privilege in new_privileges]
    # Insert a bulk of data using Core
    permission.session.execute(
        Privileges.__table__.insert(),
        new_privileges
    )
    permission.session.commit()
    return {
            "message": "New Privilege successfully registered!"
        }

""" Get all privileges info. Apply for root user. """
@admin_router.get("/privileges", response_model=List[Privileges])
async def get_all_privileges(permission: Permission = Security(scopes=["admin"]),
                                query_params: CommonQueryParams = Depends()):
    statement = select(Privileges)
    if query_params.limit != None and query_params.limit > 0:
        statement = statement.limit(query_params.limit)
    if query_params.sort != None:
        if query_params.sort[0] == "-":
            statement = statement.order_by(Privileges.privilege_name.desc())
        elif query_params.sort[0] == "+":
            statement = statement.order_by(Privileges.privilege_name.asc())
    if query_params.search != None:
        statement = statement.filter(Privileges.privilege_name.contains(query_params.search))
    privileges = permission.session.execute(statement).all()
    return [privilege[0] for privilege in privileges]
    
""" Get a specific privilege info. Apply for root user. """
@admin_router.get("/privileges/{privilege_name}", response_model=Privileges)
async def get_a_privilege_info(privilege_name: str, permission: Permission = Security(scopes=["admin"])):
    privilege = permission.session.get(Privileges, privilege_name)
    if(privilege):
        return privilege
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Privilege with supplied name does not exist"
    )
    
""" Update privilege info. Apply for root user """ 
@admin_router.put("/privileges/{privilege_name}", response_model=Privileges)
async def update_privilege_info(privilege_name: str, body: PrivilegeUpdate, 
                                    permission: Permission = Security(scopes=["admin"])):
    privilege = permission.session.get(Privileges, privilege_name)
    if privilege:
        privilege_data = body.dict(exclude_unset=True)
        for key, value in privilege_data.items():
            setattr(privilege, key, value)
            
        permission.session.add(privilege)
        permission.session.commit()
        permission.session.refresh(privilege)
        return privilege   
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Privilege with supplied name does not exist"
    )
    
""" Delete a privilege. Apply for root user. """
@admin_router.delete("/privileges/{privilege_name}")
async def delete_a_privilege(privilege_name: str, permission: Permission = Security(scopes=["admin"])):
    privilege = permission.session.get(Privileges, privilege_name)
    if privilege:
        permission.session.delete(privilege)
        permission.session.commit()
        return {
            "message": "Privilege deleted successfully"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Privilege with supplied name does not exist"
    )
    
""" Delete list of privilege. Apply for root user. """
@admin_router.delete("/privileges")
async def delete_list_privileges(privilege_names: List[str], 
                                    permission: Permission = Security(scopes=["admin"])):
    # Delete a bulk of data using Core
    permission.session.execute(
        Privileges.__table__.delete().where(Privileges.privilege_name.in_(privilege_names))
    )
    permission.session.commit()
    return {
        "message": "Privileges deleted successfully"
    }
    
""" ********************** MANIPULATE ACCOUNT_PRIVILEGES DATA.*********************** """

""" Add a new account_privilege. Apply for admin user"""
@admin_router.post("/account_privilege")
async def add_a_account_privilege(new_account_privilege: Account_Privileges, 
                                    permission: Permission = Security(scopes=["admin"])) -> dict:
    account_privilege = permission.session.execute(select(Account_Privileges).
                                        filter(Account_Privileges.privilege_name == new_account_privilege.privilege_name).
                                        filter(Account_Privileges.username == new_account_privilege.username)).first()
    if account_privilege:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account_Privilege exists"
        )
    try:
        permission.session.add(new_account_privilege)
        permission.session.commit()
        permission.session.refresh(new_account_privilege)
        return {
            "message": "New Privilege successfully registered!"
        }
    except IntegrityError as e:
        # This error when add wrong foreign key in new data
        return {
            "error": e
        }
    
""" Add a list of account_privilege. Apply for admin user"""
@admin_router.post("/account_privileges")
async def add_list_account_privileges(new_account_privileges: List[Account_Privileges], 
                                        permission: Permission = Security(scopes=["admin"])) -> dict:
    for new_account_privilege in new_account_privileges:
        account_privilege = permission.session.execute(select(Account_Privileges).
                                            filter(Account_Privileges.privilege_name == new_account_privilege.privilege_name).
                                            filter(Account_Privileges.username == new_account_privilege.username)).first()
        # print('account = ', (account is None))
        if account_privilege:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Have Account_Privilege exists"
            )

    new_account_privileges = [dict(account_privilege) for account_privilege in new_account_privileges]
    # Insert a bulk of data using Core
    try:
        permission.session.execute(
            Account_Privileges.__table__.insert(),
            new_account_privileges
        )
        permission.session.commit()
        return {
                "message": "New Privilege successfully registered!"
            }
    except IntegrityError as e:
        # This error when add wrong foreign key in new data
        return {
                "error": e
            }
    
""" Get privileges for a specific username. Apply for admin user. """
@admin_router.get("/account_privileges/{username}")
async def get_privileges_by_username(username: str, 
                                        permission: Permission = Security(scopes=["admin"]),
                                        query_params: CommonQueryParams = Depends()):
    statement = select(Account_Privileges).select_from(Privileges).join(
        Account_Privileges, Account_Privileges.privilege_name == Privileges.privilege_name).where(Account_Privileges.username == username)
    if query_params.limit != None and query_params.limit > 0:
        statement = statement.limit(query_params.limit)
    if query_params.sort != None:
        if query_params.sort[0] == "-":
            statement = statement.order_by(Account_Privileges.privilege_name.desc())
        elif query_params.sort[0] == "+":
            statement = statement.order_by(Account_Privileges.privilege_name.asc())
    if query_params.search != None:
        statement = statement.filter(Account_Privileges.privilege_name.contains(query_params.search))
    privileges_by_username = permission.session.execute(statement).all()
    privileges_by_username = [privileges[0] for privileges in privileges_by_username]
    return privileges_by_username
    
""" Delete a account_privilege by username. Apply for root user. """
@admin_router.delete("/account_privileges/{username}/{privilege_name}")
async def delete_account_privilege_by_username(username: str, privilege_name: str, 
                                               permission: Permission = Security(scopes=["admin"])):
    account_privilege = permission.session.execute(select(Account_Privileges).filter(Account_Privileges.privilege_name == privilege_name).
                                filter(Account_Privileges.username == username)).first()
    if account_privilege:
        permission.session.delete(account_privilege[0])
        permission.session.commit()
        return {
            "message": "Account_Privilege deleted successfully"
        }
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Account_Privilege does not exist"
    )
