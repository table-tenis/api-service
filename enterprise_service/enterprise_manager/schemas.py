from pydantic import BaseModel
from typing import Optional

class SiteUpdate(BaseModel):
    enterprise_id: Optional[int] 
    name: Optional[str] 
    description: Optional[str] 
    note: Optional[str] 

class CameraUpdate(BaseModel):
    site_id: Optional[int] 
    session_service_id: Optional[int]
    ip: Optional[str]
    name: Optional[str]
    description: Optional[str]
    rtsp_uri: Optional[str]
    stream: Optional[str]
