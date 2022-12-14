from time import time
from fastapi import APIRouter, HTTPException, status, Depends, Response, Security, Query
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from sqlmodel import select
from sqlalchemy.orm import load_only

from models import Account
from schemas import TokenResponse, AccountInfo, AccountBaseModel, AccountUpdatePassword

from core.database import get_session
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token

from dependencies import Authorization, get_authorization, CommonQueryParams
from core.database import redis_db, db
account_router = APIRouter( tags=["Account"] )

hash_password = HashPassword()
# """ Signin to access system info. """
@account_router.get("/auth")
async def auth(authorization: Authorization = Security()) -> dict:
    print(authorization.authorization)
    return {"Authenticate" : "OK"}

""" Add a new account. Aplly for root user. """
@account_router.post("/")
async def add_a_new_account(singup_account: Account, 
                            authorizaion: Authorization = Security(scopes=["root"]),
                            session = Depends(get_session)) -> dict:
    account = db.get_by_id(session, select(Account).where(Account.username == singup_account.username))
    if account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account Supplied Username Is Existed"
        )
    hashed_password = hash_password.create_hash(singup_account.password)
    singup_account.password = hashed_password
    singup_account = db.add(session, singup_account)
    return {
        "Response": "New Account Successfully Registered!"
    }

""" Signin to access system info. """
@account_router.post("/login", response_model=TokenResponse)
async def account_login(account: OAuth2PasswordRequestForm = Depends(), 
                        session = Depends(get_session)) -> dict:
    account_exist = db.get_by_id(session, select(Account).where(Account.username == account.username))
    if not account_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username Or Password Wrong"
        )
    if hash_password.verify_hash(account.password, account_exist.password):
        access_token = create_access_token(account_exist.username, get_authorization(account_exist.username, session))
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Username Or Password Wrong"
    )

""" Signin to access system info. """
@account_router.get("/logout")
async def account_logout(authorization: Authorization = Security()) -> dict:
    try:
        redis_db.set(authorization.token, authorization.username)
    except Exception as e:
        raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = str(e)
            )
    expire_time = authorization.expires - time()
    if expire_time > 0:
        redis_db.expire(authorization.token, int(expire_time))
    return {
        "Response": "Logout Success"
    }
    
""" Get all account's username info. Apply for root user. """
@account_router.get("/" )
async def get_accounts(username: str = Query(default=None),
                        authorization: Authorization = Security(),
                        sorted: str = Query(default=None, regex="^[+-](username)"),
                        search: str = Query(default=None, regex="(username|email|cellphone|note)-"),
                        limit: int = Query(default=None, gt=0),
                        session = Depends(get_session)):
    statement = select(Account)
    if username != None:
        if not authorization.is_root and username != authorization.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Username Does Not Match"
            )
        statement = statement.where(Account.username == username)
    elif username == None and not authorization.is_root:
        # Just retrieve account for only this sign-in account
        statement = statement.where(Account.username == authorization.username)
    
    if search != None:
        search = search.split('-')
        if search[1] != '':
            if search[0] == 'username':
                statement = statement.filter(Account.username.contains(search[1]))
            elif search[0] == 'email':
                statement = statement.filter(Account.email.contains(search[1]))
            elif search[0] == 'cellphone':
                statement = statement.filter(Account.cellphone.contains(search[1]))
            elif search[0] == 'note':
                statement = statement.filter(Account.note.contains(search[1]))
    if sorted != None:
        if sorted[0] == "-":
            if sorted[1:] == 'username':
                statement = statement.order_by(Account.username.desc())
        elif sorted[0] == "+":
            if sorted[1:] == 'username':
                statement = statement.order_by(Account.username.asc())
    if limit != None and limit > 0:
        statement = statement.limit(limit)
        
    accounts = db.get_all(session, statement)
    if not accounts:
        return {"Response": "Not Found"}
    # acc = AccountInfo()
    return [{"username":account[0].username, "email":account[0].email, 
             "cellphone":account[0].cellphone, "note":account[0].note, 
             "is_root":account[0].is_root} for account in accounts]
   
""" Update account info itself. """ 
@account_router.put("/", response_model=AccountInfo)
async def update_account_info(body: AccountBaseModel, 
                              username: str = Query(),
                              authorization: Authorization = Security(),
                              session = Depends(get_session)) -> Account:
    if username == authorization.username or authorization.is_root:
        account_exist = db.get_by_id(session, select(Account).where(Account.username == username))
        if account_exist:
            account_data = body.dict(exclude_unset=True)
            for key, value in account_data.items():
                setattr(account_exist, key, value)
              
            account_exist = db.add(session, account_exist)  
            return account_exist 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Account Supplied Username Does Not Exist"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission Denied"
        )

""" Change account password itself. """
@account_router.put("/changepassword")
async def change_account_password(body: AccountUpdatePassword, 
                                  username: str = Query(),
                                  authorization: Authorization = Security(), 
                                  session = Depends(get_session)):
    if username == authorization.username or authorization.is_root:
        account_exist = db.get_by_id(session, select(Account).where(Account.username == username))
        if account_exist:
            account_data = body.dict(exclude_unset=True)
            for key, value in account_data.items():
                setattr(account_exist, key, value)
        
            hashed_password = hash_password.create_hash(body.password)
            account_exist.password = hashed_password
            account_exist = db.add(session, account_exist)
            return {"Response": "Changed Password Success"}    
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Account Supplied Username Does Not Exist"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission Denied"
        )
        
""" Delete an account. Apply for root user. """
@account_router.delete("/")
async def delete_account(username: str = Query(), 
                         authorization: Authorization = Security(scopes=["root"]),
                         session = Depends(get_session)):
    account = db.get_by_id(session, select(Account).where(Account.username == username))
    if account:
        db.delete(session, account)
        return {
            "Response": "Account Deleted Successfully"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Account Supplied Username Does Not Exist"
    )