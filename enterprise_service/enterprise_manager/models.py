from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON

class EnterpriseBase(SQLModel):
    enterprise_code: str = Field(default=None)
    name: str = Field(default=None)
    email: str = Field(default=None)
    note: str = Field(default=None)
    
class Enterprise(EnterpriseBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "id": "default = None, auto increase",
                "enterprise_code": "vtx",
                "name": "Vien Hang Khong Vu Tru Viettel",
                "email": "vtx@vtx",
                "note": "vtx is vtx"
            }
        }
     
class SiteBase(SQLModel):
    enterprise_id: int
    name: str = Field(default=None)
    description: str = Field(default=None)
    note: str = Field(default=None)
    class Config:
        schema_extra = {
            "example": {
                "enterprise_id": 1,
                "name": "20 tang",
                "description": "site descrtiption",
                "note": "site note"
            }
        }
   
class Site(SiteBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "id": "default = None, auto increase",
                "enterprise_id": 1,
                "name": "site name",
                "description": "site description",
                "note": "site note"
            }
        }
     
class CameraBase(SQLModel):
    site_id: int 
    session_service_id: int = Field(default=None)
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
                "id": "default = None, auto increase",
                "site_id": 1,
                "ip": "172.21.104.100",
                "name": "AI Camera",
                "description": "floor 4...",
                "rtsp_uri": "rtsp://172.21.104.100:554/main,rtsp://172.21.104.100:554/sub",
                "stream": "encoding/H264/width/3840/height/2160/framerate_limit/5/bitrate_limit/3072,"\
                          "encoding/H264/width/640/height/480/framerate_limit/25/bitrate_limit/512"
            }
        }