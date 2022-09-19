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
from json import loads
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

class Authorization:
    def __init__(self, request: Request, security_scopes: SecurityScopes, 
                 auth: dict = Depends(authenticate)) -> None:
        self.scopes = security_scopes.scopes
        self.authorization = loads(auth['decoded_token']['authorization'])
        self.username = auth.get('decoded_token').get('username')
        self.is_root = self.authorization['is_root']
        self.key = []
        if 'root' in self.scopes and self.is_root == False:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Permission Denied"
            )
        if self.is_root:
            self.key.append('*')
        if ('root' not in self.scopes) and (not self.is_root) and (len(self.scopes) > 0):
            # find all key this account can access
            acls = self.authorization['acl'].split('|')
            tag_type = self.scopes[0]
            permission_required = self.scopes[1]
            acl = ''
            for i in range(len(acls)):
                if tag_type == acls[i].split(':')[0]:
                    acl = acls[i]
                    break
            # This just find id access with match entire tag_type
            if acl != '':
                tag_qualifier_valid = []
                acl_accquired = acl.split(':') # ['enterprise.site', '1.1,1.2,1.3', 'crud,admin,cru-']
                tag_qualifier_accquired = acl_accquired[1].split(',') # ['1.1', '1.2', '1.3']
                permissions_accquired = acl_accquired[2].split(',') # ['crud', 'admin', 'cru-']
                for i in range(len(permissions_accquired)):
                    if permission_required in permissions_accquired[i] or 'admin' == permissions_accquired[i]:
                        tag_qualifier_valid.append(tag_qualifier_accquired[i])
                tag_qualifier_valid = [tag_qualifier.split('.') for tag_qualifier in tag_qualifier_valid]
                for tag_qualifier in tag_qualifier_valid:
                    # convert list of str to list of int
                    try:
                        self.key.append([int(i) for i in tag_qualifier])
                    except ValueError as e:
                        print(e)

            # try to match sub tag_type with 'admin' permission
            # else:
            tag_type_separate = tag_type.split('.')
            sub_acl = []
            sub_acl_len_reserve = {}
            if len(tag_type_separate) > 1:
                for i in range(1, len(tag_type_separate)):
                    sub_tag_type = '.'.join(tag_type_separate[:-i])
                    # Match sub_tag_type with all tag_type in acl records
                    for j in range(len(acls)):
                        if sub_tag_type == acls[j].split(':')[0]:
                            # If Match, save this sub_tag_type with sub_len_reserve
                            # Example: origin tag_type = 'enterprise.site.camera'
                            # matched sub_tag_type  = 'enterprise.site', sub_len_reserve = 1
                            # Or matched sub_tag_type  = 'enterprise', sub_len_reserve = 2
                            # sub_len_reserve to add '-1' id as accept all id to tag_qualifier list
                            # If scope require is 'enterprise.site.camera'
                            # And if matched sub_tag_type  = 'enterprise.site' with tag_qualifier = '1.2', so tag_qualifier list = [1,2,-1]
                            # Or if matched sub_tag_type  = 'enterprise' with tag_qualifier = '1', so tag_qualifier list = [1,-1,-1]
                            sub_acl.append(acls[j])
                            sub_acl_len_reserve[acls[j]] = i
                            break
            for acl in sub_acl:
                tag_qualifier_valid = []
                acl_accquired = acl.split(':') # ['enterprise.site', '1.1,1.2,1.3', 'crud,admin,cru-'] or ['enterprise', '1,2', 'admin,admin']
                tag_qualifier_accquired = acl_accquired[1].split(',') # ['1.1', '1.2', '1.3']
                permissions_accquired = acl_accquired[2].split(',') # ['crud', 'admin', 'cru-']
                for i in range(len(permissions_accquired)):
                    if 'admin' == permissions_accquired[i]:
                        tag_qualifier_valid.append(tag_qualifier_accquired[i])
                tag_qualifier_valid = [tag_qualifier.split('.') for tag_qualifier in tag_qualifier_valid]
                for tag_qualifier in tag_qualifier_valid:
                    # convert list of str to list of int
                    for j in range(sub_acl_len_reserve[acl]):
                        tag_qualifier.append('-1')
                    try:
                        self.key.append([int(i) for i in tag_qualifier])
                    except ValueError as e:
                        print(e)

            
        print("key = ", self.key)
        if len(self.key) == 0 and (len(self.scopes) > 0):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Permission Denied!"
            )

            
            
        