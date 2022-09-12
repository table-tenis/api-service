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

class TokenResponse(BaseModel):
    access_token: str
    token_type: str