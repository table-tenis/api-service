from pydantic import BaseModel
from typing import Optional
from datetime import date

class SiteUpdate(BaseModel):
    name: Optional[str] 
    description: Optional[str] 
    note: Optional[str] 

class CameraUpdate(BaseModel):
    site_id: Optional[int] 
    ip: Optional[str]
    name: Optional[str]
    description: Optional[str]
    rtsp_uri: Optional[str]
    stream: Optional[str]
    
class StaffUpdate(BaseModel):
    staff_code: Optional[str]
    email_code: Optional[str]
    unit: Optional[str]
    title: Optional[str]
    fullname: Optional[str]
    nickname: Optional[str]
    cellphone: Optional[str]
    date_of_birth: Optional[str]
    sex: Optional[str]
    state: Optional[int]
    notify_enable: Optional[bool]
    note: Optional[str]
