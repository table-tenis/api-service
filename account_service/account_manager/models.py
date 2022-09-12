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
      
class PrivilegeBase(SQLModel):
    description: Optional[str]
    
class Privileges(PrivilegeBase, table=True):
    privilege_name: str = Field(primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "privilege_name": "P1",
                "description": "access staffs"
            }
        }

class PrivilegeUpdate(PrivilegeBase):
    pass
   
class Account_Privileges(SQLModel, table=True):
    username: str = Field(primary_key=True)
    privilege_name: str = Field(primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "username": "tainp",
                "privilege_name": "x_priv_staff"
            }
        }
        
class AccountPrivilegesInfo(SQLModel):
    username: str
    privilege_name: str
    description: str
    class Config:
        schema_extra = {
            "example": {
                "username": "tainp",
                "privilege_name": "x_priv_staff",
                "description": ""
            }
        }