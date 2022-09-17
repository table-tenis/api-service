from fastapi import APIRouter, HTTPException, status, Depends, Query, Request, Security, Path
from fastapi.security import OAuth2PasswordRequestForm
from rsa import verify
from sqlmodel import Session, select
from sqlalchemy.orm import load_only
from core.database import get_session
from auth.authenticate import authenticate
from models import Account, ACL
from fastapi.security import (
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from json import loads

SQLALCHEMY_ERROR = {
    'l7de': 'UnsupportedCompilationError',
    'xd1r': 'AwaitRequired',
    'xd2s': 'MissingGreenlet',
    'dbapi': 'DBAPIError',
    'rvf5': 'InterfaceError',
    '4xp6': 'DatabaseError',
    '9h9h': 'DataError',
    'e3q8': 'OperationalError',
    'gkpj': 'IntegrityError',
    '2j85': 'InternalError',
    'f405': 'ProgrammingError',
    'tw8g': 'NotSupportedError'
}
SQLALCHEMY_ERROR_DETAIL = {
    'l7de': 'Raised when an operation is not supported by the given compiler',
    'xd1r': 'Error raised by the async greenlet spawn if no async operation was awaited when it required one',
    'xd2s': 'Error raised by the async greenlet await\_ if called while not inside the greenlet spawn context',
    'dbapi': 'Raised when the execution of a database operation fails',
    'rvf5': 'Raised when the Interface execution of a database operation fails',
    '4xp6': 'Raised when the Database execution of a database operation fails',
    '9h9h': 'Raised when the Data execution of a database operation fails',
    'e3q8': 'Raised when the Operational execution of a database operation fails',
    'gkpj': 'Raised when the Integrity execution of a database operation fails',
    '2j85': 'Raised when the Internal execution of a database operation fails',
    'f405': 'Raised when the Programming execution of a database operation fails',
    'tw8g': 'Raised when the Programming execution of a database operation fails'
}

def get_error(e):
    return {'type': SQLALCHEMY_ERROR.get(e.code), 'detail': SQLALCHEMY_ERROR_DETAIL.get(e.code),
                'error': e._message()}
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
        self.token = auth['token']
        self.authorization = loads(auth['decoded_token']['authorization'])
        self.username = auth.get('decoded_token').get('username')
        self.expires = auth.get('decoded_token').get('expires')
        self.is_root = self.authorization['is_root']
        self.key = []
        if 'root' in self.scopes and self.is_root == False:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Permission Denied!"
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
            if acl != '':
                acl_accquired = acl.split(':')
                tag_qualifier_accquired = acl_accquired[1].split(',')
                permissions_accquired = acl_accquired[2].split(',')
                for i in range(len(permissions_accquired)):
                    if permission_required in permissions_accquired[i] or 'admin' == permissions_accquired[i]:
                        self.key.append(tag_qualifier_accquired[i])
                self.key = [tuple(tag_qualifier.split('.')) for tag_qualifier in self.key]
            
            # print("key = ", self.key, ", acl = ", acl)

def get_authorization(username: str, session):
    account = session.get(Account, username)
    authorization = {}
    if account.is_root:
        authorization['is_root'] = True
        return authorization
    else:
        authorization['is_root'] = False
    acl_list = []
    statement = select(ACL).where(ACL.username == username)
    acls = session.execute(statement).all()
    tag_type_list = []
    tag_qualifier_list = []
    permissions_list = []
    for acl in acls:
        if acl[0].tag_type not in tag_type_list:
            tag_type_list.append(acl[0].tag_type)
            tag_qualifier_list.append(acl[0].tag_qualifier)
            permissions_list.append(acl[0].permissions)
        else:
            index = tag_type_list.index(acl[0].tag_type)
            tag_qualifier_list[index] += "," + acl[0].tag_qualifier
            permissions_list[index] += "," + acl[0].permissions
    for i in range(len(tag_type_list)):
        acl_list.append(tag_type_list[i]+":"+tag_qualifier_list[i]+":"+permissions_list[i])
    authorization['acl'] = "|".join(acl_list)
    # print("acl_list = ", acl_list)
    # print("authorization['acl'] = ", authorization['acl'])
    return authorization
            

            
            
        