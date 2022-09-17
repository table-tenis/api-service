from pydantic import BaseModel
from typing import Optional

class AccountBaseModel(BaseModel):
    email: Optional[str]
    cellphone: Optional[str]
    note: Optional[str]
    
class AccountInfo(AccountBaseModel):
    username: str
    is_root: bool
        
class AccountUpdatePassword(BaseModel):
    password: str

class ACLUpdate(BaseModel):
    tag_type: Optional[str]
    tag_qualifier: Optional[str]
    permissions: Optional[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str