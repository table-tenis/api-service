from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import date
from core.helper import str_to_date

class ReportBase(SQLModel):
    staff_id: int = Field(default=None)
    checkin: str = Field(default=None)
    checkout: str = Field(default=None)
    report_date: str = Field(default=None)
    
class Report(ReportBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "id": "default = None, auto increase",
                "staff_id": 1,
                "checkin": "checkin time",
                "checkout": "checkout time",
                "report_date": "report date time"
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
                "description": "floor 4...",
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
class Staff(StaffBase, table=True):
    id: int = Field(default=None, primary_key=True)
    class Config:
        schema_extra = {
            "example": {
                "staff_code": "xxxxxx",
                "email_code": "xxxxxx",
                "unit": "TT DTDQDT",
                "title": "system engineer",
                "fullname": "Nguyen Van xxxxxx",
                "nickname": "xxxxxx",
                "date_of_birth": str_to_date("2000-11-12"),
                "sex": "male",
                "state": 1,
                "notify_enable": True,
                "note": "xxxxx"
            }
        }
        
class DetectionBase(SQLModel):
    staff_id: int = Field(default=None)
    cam_id: int = Field(default=None)
    session_id: str = Field(default=None)
    frame_id: int = Field(default=None)
    detection_time: str = Field(default=None)
    detection_score: float = Field(default=None)
    blur_score: float = Field(default=None)
    box_x: float = Field(default=None)
    box_y: float = Field(default=None)
    box_width: float = Field(default=None)
    box_height: float = Field(default=None)
    has_mask: bool = Field(default=None)
    has_pose: bool = Field(default=None)
    feature: str = Field(default=None)
    uri_image: str = Field(default=None)
    polygon_face: str = Field(default=None)
class Detection(DetectionBase, table=True):
    id: int = Field(default=None, primary_key=True)