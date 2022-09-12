from time import time
from fastapi import APIRouter, HTTPException, status, Depends, Response, Security
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from sqlmodel import select
from sqlalchemy.orm import load_only

from models import Account
from schemas import TokenResponse, AccountInfo, AccountBaseModel, AccountUpdatePassword

from core.database import get_session
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from auth.authenticate import authenticate

from dependencies import Authorization, get_authorization, CommonQueryParams
from core.database import redis_db
account_router = APIRouter( tags=["Account"] )

hash_password = HashPassword()

""" Signin to access system info. """
@account_router.get("/auth")
async def auth(user_auth: dict = Depends(authenticate),
               autho: Authorization = Security(scopes=['root'])) -> dict:
    print(autho.autho)
    return {"Authenticate" : "OK"}

""" Add a new account. Aplly for root user. """
@account_router.post("/")
async def add_a_new_account(singup_account: Account, 
                            autho: Authorization = Security(scopes=["root"]),
                            session = Depends(get_session)) -> dict:
    account = session.execute(select(Account).where(Account.username == singup_account.username)).first()
    if account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account with supplied username exists"
        )
    hashed_password = hash_password.create_hash(singup_account.password)
    singup_account.password = hashed_password
    session.add(singup_account)
    session.commit()
    session.refresh(singup_account)
    return {
        "message": "New Account successfully registered!"
    }

""" Signin to access system info. """
@account_router.post("/login", response_model=TokenResponse)
async def account_login(account: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)) -> dict:
    account_exist = session.get(Account, account.username)
    if not account_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with username does not exist."
        )
    if hash_password.verify_hash(account.password, account_exist.password):
        access_token = create_access_token(account_exist.username, get_authorization(account_exist.username, session))
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid details passed."
    )

""" Signin to access system info. """
@account_router.get("/logout")
async def account_logout(auth: dict = Depends(authenticate)) -> dict:
    redis_db.set(auth.get("token"), auth.get("decoded_token").get("username"))
    expire_time = auth.get("decoded_token").get("expires") - time()
    if expire_time > 0:
        redis_db.expire(auth.get("token"), int(expire_time))
    return {
        "Logout success"
    }
    
""" Get all account's username info. Apply for root user. """
@account_router.get("/", response_model=List[AccountInfo])
async def get_accounts(autho: Authorization = Security(scopes=["root"]),
                        query_params: CommonQueryParams = Depends(),
                        session = Depends(get_session)):
    statement = select(Account)
    if query_params.limit != None and query_params.limit > 0:
        statement = statement.limit(query_params.limit)
    if query_params.sort != None:
        if query_params.sort[0] == "-":
            statement = statement.order_by(Account.username.desc())
        elif query_params.sort[0] == "+":
            statement = statement.order_by(Account.username.asc())
    if query_params.search != None:
        statement = statement.filter(Account.username.contains(query_params.search))
    accounts = session.execute(statement).all()
    list_account = []
    for account in accounts:
        list_account.append(account[0])
    return list_account

""" Get account info itself. """
@account_router.get("/{username}", response_model=AccountInfo)
async def get_account_info(username: str, autho: Authorization = Security(scopes=[]),
                           session = Depends(get_session)):
    if username == autho.username or autho.is_root:
        account_exist = session.get(Account, username)
        if account_exist:
            return account_exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with supplied username does not exist"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username does not match athentication"
        )
   
""" Update account info itself. """ 
@account_router.put("/{username}", response_model=AccountInfo)
async def update_account_info(username: str, body: AccountBaseModel, 
                              autho: Authorization = Security(),
                              session = Depends(get_session)) -> Account:
    if username == autho.username or autho.is_root:
        account_exist = session.get(Account, username)
        if account_exist:
            account_data = body.dict(exclude_unset=True)
            for key, value in account_data.items():
                setattr(account_exist, key, value)
                
            session.add(account_exist)
            session.commit()
            session.refresh(account_exist)
            return account_exist 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Account with supplied username does not exist"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username does not match athentication"
        )

""" Change account password itself. """
@account_router.put("/{username}/changepassword", response_model=AccountInfo)
async def change_account_password(username: str, body: AccountUpdatePassword, 
                                  autho: Authorization = Security(),
                                  session = Depends(get_session)) -> Account:
    if username == autho.username or autho.is_root:
        account_exist = session.get(Account, username)
        if account_exist:
            account_data = body.dict(exclude_unset=True)
            for key, value in account_data.items():
                setattr(account_exist, key, value)
        
            hashed_password = hash_password.create_hash(body.password)
            account_exist.password = hashed_password
            session.add(account_exist)
            session.commit()
            session.refresh(account_exist)
            return account_exist    
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Account with supplied username does not exist"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username does not match athentication"
        )
        
""" Delete an account. Apply for root user. """
@account_router.delete("/{username}")
async def delete_account(username: str, autho: Authorization = Security(scopes=["root"]),
                         session = Depends(get_session)):
    account = session.get(Account, username)
    if account:
        session.delete(account)
        session.commit()
        return {
            "message": "Account deleted successfully"
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Account with supplied username does not exist"
    )