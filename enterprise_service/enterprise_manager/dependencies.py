from fastapi import APIRouter, HTTPException, status, Depends, Query, Request, Security, Path
from fastapi.security import OAuth2PasswordRequestForm
from rsa import verify
from sqlmodel import select
from sqlalchemy.orm import load_only
from core.database import get_session
from auth.authenticate import authenticate
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
import struct, json
from difflib import SequenceMatcher
class CommonQueryParams:
    def __init__(self, limit: int = Query(default=None, description="set limit number account's username to retrieve", gt=0),
                                        sort: str = Query(default=None, regex="^[+-].*"),
                                        search: str = Query(default=None)):
        self.sort = sort
        self.limit = limit
        self.search = search
        
class PathParams:
    def __init__(self, enterprise_id: int = Path(default=None, gt=0), site_id: int = Path(default=None)):
        self.enterprise_id = enterprise_id
        self.site_id = site_id
 
class CommonDepend:
    def __init__(self, session = Depends(get_session)):
        self.session = session

class OAuth2PasswordPermission(CommonDepend):
    username: str
    password: str
    def __init__(self, account: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)):
        super().__init__(session)
        self.username = account.username
        self.password = account.password

class LogoutPermission(CommonDepend):
    username: str
    expires: float
    token: str
    def __init__(self, session = Depends(get_session), user_auth: dict = Depends(authenticate)):
        super().__init__(session)
        self.username = user_auth.get("decoded_token").get("username")
        self.expires = user_auth.get("decoded_token").get("expires")
        self.token = user_auth.get("token")
            
class Permission(CommonDepend):
    privileges: list # List of privileges from database
    unique_permisson: list  # List of Permissons
    unique_permisson_suited: list  # List of Permissons
    permission_action: dict # Dict of Permissions and its action. Like {"enterprise:1.staff" : ['read', 'create', 'delete', 'update']}
    unique_permisson_full: list
    permissions_id: dict
    def __init__(self, request: Request, security_scopes: SecurityScopes, session = Depends(get_session), user_auth: dict = Depends(authenticate)) -> None:
        super().__init__(session)
        self.privileges = []
        self.unique_permisson = []
        self.unique_permisson_suited = []
        self.permission_action = {}
        self.unique_permisson_full = []
        self.scopes = security_scopes.scopes
        self.scopes_permission = security_scopes.scopes[:-1]
        self.action_require = security_scopes.scopes[-1]
        self.permissions_id = {}
        self.username = user_auth.get("decoded_token").get("username")
        # self.expires = user_auth.get("decoded_token").get("expires")

            
            
        