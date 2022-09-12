from fastapi import APIRouter, HTTPException, status, Depends, Query, Request, Security, Path
from fastapi.security import OAuth2PasswordRequestForm
from rsa import verify
from sqlmodel import Session, select
from sqlalchemy.orm import load_only
from core.database import get_session
from auth.authenticate import authenticate
from models import Account, Privileges, Account_Privileges
from fastapi.security import (
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from json import loads
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
class Authorization:
    def __init__(self, request: Request, security_scopes: SecurityScopes, 
                 auth: dict = Depends(authenticate)) -> None:
        self.scopes = security_scopes.scopes
        self.autho = loads(auth['decoded_token']['authorization'])
        self.username = auth.get('decoded_token').get('username')
        self.is_root = self.autho['is_root']
        print(self.autho)
        if 'root' in self.scopes and self.is_root == False:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Permission Denied!"
            )   
        
def get_authorization(username: str, session):
    account = session.get(Account, username)
    authorization = {}
    if account.is_root:
        authorization['is_root'] = True
    else:
        authorization['is_root'] = False
    return authorization
class Permission:
    privileges: list # List of privileges from database
    unique_permisson: list  # List of Permissons
    unique_permisson_suited: list  # List of Permissons
    permission_action: dict # Dict of Permissions and its action. Like {"enterprise:1.staff" : ['read', 'create', 'delete', 'update']}
    unique_permisson_full: list
    permissions_id: dict
    def __init__(self, request: Request, security_scopes: SecurityScopes, session = Depends(get_session), user_auth: dict = Depends(authenticate)) -> None:
        self.session = session 
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
        account = self.session.get(Account, self.username)
        if account.is_root:
            self.is_root = True
        else:
            self.is_root = False
           
        """ Admin account always pass permission. """ 
        if not self.is_root:
            """ Verify Permission """
            self.permisson_verify(request) 
                    
    def permisson_verify(self, request: Request):
        if len(self.scopes) == 0:
            return
        
        if "admin" in self.scopes:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Permission Denied!"
            )
        else:
            """ Verify permission from account that is not admin"""
            self.privileges = []
            statement = select([Account_Privileges.privilege_name, Privileges.description]).select_from(Privileges).join(
                Account_Privileges, Account_Privileges.privilege_name == Privileges.privilege_name).where(Account_Privileges.username == self.username)
            privileges_list = self.session.execute(statement).all()
            if len(privileges_list) == 0:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Permission Denied!"
                )
            self.privileges = [{"privilege_name": priv[0], "description": priv[1]} for priv in privileges_list]
            print("---------------- privileges = ", self.privileges)
            permisson_action_separates = []
            permissons = []
            for privilege in self.privileges:
                # priv_name = privilege["privilege_name"].split("_")[1]
                try:
                    list_str_priv = privilege["privilege_name"].split(".")
                    action = list_str_priv[-1]
                    priv_type = ".".join(list_str_priv[:-1])
                    permisson_action_separates.append({priv_type: action})
                    permissons.append(priv_type)
                except ValueError as e:
                    print("Permission wrong type: ", e)
            for permission in permissons:
                if permission not in self.unique_permisson:
                    self.unique_permisson.append(permission)
                    if len(permission.split(".")) == len(self.scopes_permission):
                        self.unique_permisson_suited.append(permission)
                           
            for per in self.unique_permisson:
                self.permission_action[per] = [per_act.get(per) for per_act in permisson_action_separates 
                                               if (per_act.get(per) != None and per_act.get(per) != "")]
                self.unique_permisson_full.append(per + "." + ".".join(self.permission_action[per]))
                
            """ After get dict of permission and action. """
            """ Get permission match to scope's permisson. """
            print("==================== permission_action = ", self.permission_action)
            print("==================== unique_permisson_suited = ", self.unique_permisson_suited)
            print("==================== unique_permisson_full = ", self.unique_permisson_full)
            if len(self.unique_permisson_suited) == 0:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Permission Denied!"
                )
                
            permission_match_list: list = []
            for permission in self.unique_permisson_suited:
                separate_match = []
                for scope in self.scopes_permission:
                    if scope in permission:
                        separate_match.append(True)
                    else:
                        separate_match.append(False)
                if not False in separate_match:
                    permission_match_list.append(permission)
                
            if len(permission_match_list) == 0:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Permission Denied!"
                )
            
            permission_action_match_list: list = []
            for permission_match in permission_match_list:
                actions = self.permission_action.get(permission_match)
                print("================ permission_match = ", permission_match)
                print("================ actions = ", actions)
                if "all" not in actions and "*" not in actions:   
                    if self.action_require == "all" or self.action_require == "*":
                        print("Not all or * in actions")
                        continue
                        
                    elif (self.action_require == "read") and ("read" not in actions):
                        continue
                        
                    elif (self.action_require == "create") and ("create" not in actions):
                        continue
                        
                    elif (self.action_require == "update") and ("update" not in actions):
                        continue
                        
                    elif (self.action_require == "delete") and ("delete" not in actions):
                        continue
                permission_action_match_list.append(permission_match)
                
            if len(permission_action_match_list) == 0:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Permission Denied!"
                )
        
            permission_id = {}
            print("permission_action_match_list = ", permission_action_match_list)
            for permission_action_match in permission_action_match_list:
                separate_per_list = permission_action_match.split(".")
                for separate_per in separate_per_list:
                    if ":" in separate_per:
                        per_name = separate_per.split(":")[0]
                        id = separate_per.split(":")[1]
                        if permission_id.get(per_name) == None:
                            permission_id[per_name] = [id]
                        else:
                            permission_id[per_name].append(id)
            permission_match_id_str = []
            for key, value in permission_id.items():
                permission_match_id_str.append(key + "." + ".".join(value))
                
            for permission_match_id in permission_match_id_str:
                if "enterprise" in permission_match_id:
                    self.permissions_id["enterprise"] = [int(i) for i in permission_match_id.split(".")[1:]]
                    
                if "site" in permission_match_id:
                    self.permissions_id["site"] = [int(i) for i in permission_match_id.split(".")[1:]]
                
            """ Final step. Verify path params if it included in endpoint """ 
            print("permission_id = ", permission_id)
            path_params = request.path_params
            if path_params.get("enterprise_id") != None:
                if not self.match_path_param("enterprise", path_params.get("enterprise_id"), permission_match_id_str):
                    raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Permission Denied!"
                )
                print("Enterprise Id Match")
                
            if path_params.get("site_id") != None:
                if not self.match_path_param("site", path_params.get("site_id"), permission_match_id_str):
                    raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Permission Denied!"
                )
                print("Site Id Match")
                
    def match_path_param(self, pattern, value, permission_match_id_str):
        for permission_match_id in permission_match_id_str:
            if pattern in permission_match_id:
                if value in permission_match_id.split(".")[1:]: 
                    return True
        return False
            

            
            
        