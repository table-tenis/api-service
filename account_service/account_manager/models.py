from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON

class AccountBase(SQLModel):
    email: Optional[str]
    cellphone: Optional[str]
    note: Optional[str]
    
class Account(AccountBase, table=True):
    username: str = Field(default=None, primary_key=True)
    password: str
    is_root: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": {
                "username": "tainp",
                "password": "strong!",
                "email": "tainp@gmail.com",
                "cellphone": "096322226666",
                "note": "something about user",
                "is_root": False
            }
        }

class ACLBase(SQLModel):
    username: str
    tag_type: str
    tag_qualifier: Optional[str]
    permissions: str

class ACL(ACLBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "id": "Default = None, auto increase",
                "username": "admin",
                "tag_type": "enterprise",
                "tag_qualifier": "1",
                "permissions": "admin"
            }
        }