from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import date
from core.helper import str_to_date
class EnterpriseBase(SQLModel):
    enterprise_code: str = Field(default=None)
    name: str = Field(default=None)
    email: str = Field(default=None)
    about: str = Field(default=None)
    address: str = Field(default=None)
    phone: str = Field(default=None)
    official_page: str = Field(default=None)
    note: str = Field(default=None)
    class Config:
        schema_extra = {
            "example": {
                "enterprise_code": "vtx",
                "name": "Vien Hang Khong Vu Tru Viettel",
                "email": "vtx@vtx",
                "about": "about vtx",
                "address": "address information",
                "phone": "hotline number",
                "official_page": "web page, facebook page",
                "note": "note about vtx"
            }
        }
    
class Enterprise(EnterpriseBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "enterprise_code": "vtx",
                "name": "Vien Hang Khong Vu Tru Viettel",
                "email": "vtx@vtx",
                "about": "about vtx",
                "address": "address information",
                "phone": "hotline number",
                "official_page": "web page, facebook page",
                "note": "note about vtx"
            }
        }
     
class SiteBase(SQLModel):
    name: str = Field(default=None)
    description: str = Field(default=None)
    note: str = Field(default=None)
    class Config:
        schema_extra = {
            "example": {
                "name": "site name",
                "description": "site description",
                "note": "site note"
            }
        }
   
class Site(SiteBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "name": "site name",
                "description": "site description",
                "note": "site note"
            }
        }
     
class CameraBase(SQLModel):
    site_id: int = Field(default=None)
    ip: str = Field(default="")
    name: str = Field(default=None)
    description: str = Field(default=None)
    rtsp_uri: str = Field(default=None)
    stream: str = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "site_id": 1,
                "ip": "172.21.104.100",
                "name": "AI Camera",
                "description": "floor 4...",
                "rtsp_uri": "rtsp://172.21.104.100:554/main,rtsp://172.21.104.100:554/sub",
                "stream": "encoding/H264/width/3840/height/2160/framerate_limit/5/bitrate_limit/3072,"\
                          "encoding/H264/width/640/height/480/framerate_limit/25/bitrate_limit/512"
            }
        }
   
class Camera(CameraBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "site_id": 1,
                "ip": "172.21.104.100",
                "name": "AI Camera",
                "description": "floor 4",
                "rtsp_uri": "rtsp://172.21.104.100:554/main,rtsp://172.21.104.100:554/sub",
                "stream": "encoding/H264/width/3840/height/2160/framerate_limit/5/bitrate_limit/3072,"\
                          "encoding/H264/width/640/height/480/framerate_limit/25/bitrate_limit/512"
            }
        }
        
class StaffBase(SQLModel):
    staff_code: str = Field(default=None)
    email_code: str = Field(default=None)
    unit: str = Field(default=None)
    title: str = Field(default=None)
    fullname: str = Field(default=None)
    nickname: str = Field(default=None)
    cellphone: str = Field(default=None)
    date_of_birth: date = Field(default=None)
    sex: str = Field(default=None)
    state: int = Field(default=None)
    notify_enable: bool = Field(default=None)
    note: str = Field(default=None)
    class Config:
        schema_extra = {
            "example": {
                "staff_code": "277447",
                "email_code": "tainp",
                "unit": "TT DTDQDT",
                "title": "system engineer",
                "fullname": "Nguyen Van T",
                "nickname": "t_vippro",
                "cellphone": "0123456789",
                "date_of_birth": str_to_date("2000-11-12"),
                "sex": "male",
                "state": 1,
                "notify_enable": True,
                "note": "note about stafff"
            }
        }
class Staff(StaffBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "staff_code": "277447",
                "email_code": "tainp",
                "unit": "TT DTDQDT",
                "title": "system engineer",
                "fullname": "Nguyen Van T",
                "nickname": "t_vippro",
                "cellphone": "0123456789",
                "date_of_birth": str_to_date("2000-11-12"),
                "sex": "male",
                "state": 1,
                "notify_enable": True,
                "note": "note about stafff"
            }
        }