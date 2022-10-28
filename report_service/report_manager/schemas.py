from asyncio import QueueEmpty
from typing import Optional
from datetime import date, datetime

import typing
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class MetaData:
    limit: Optional[int] = None
    offset: Optional[int] = None
    size: Optional[int] = None

""" Base Schema"""
@strawberry.type
class ReportSchema:
    id: Optional[int] = None
    staff_id: Optional[int] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    report_date: Optional[str] = None
    
@strawberry.type
class StaffSchema:
    id: int
    staff_code: Optional[str] = None
    email_code: Optional[str] = None
    fullname: Optional[str] = None
    title: Optional[str] = None
    unit: Optional[str] = None
    nickname: Optional[str] = None
    cellphone: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    state: Optional[int] = None
    notify_enable: Optional[bool] = None
    note: Optional[str] = None

@strawberry.type
class CameraSchema:
    id: Optional[int] = None
    site_id: Optional[int] = None
    ip: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    rtsp_uri: Optional[str] = None
    stream: Optional[str] = None
    
@strawberry.type
class DetectionSchema:
    session_id: Optional[str] = None
    frame_id: Optional[int] = None
    detection_time: Optional[datetime] = None
    detection_score: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    w: Optional[float] = None
    h: Optional[float] = None
    feature: Optional[str] = None
    uri_image: Optional[str] = None
  
""" Combine Schemas"""  
@strawberry.type
class CameraDetectionSchema(CameraSchema, DetectionSchema):
    pass
@strawberry.type
class CommonReport(StaffSchema):
    report: Optional[typing.List[ReportSchema]]

@strawberry.type
class StaffReport(StaffSchema):
    camera_detection: Optional[typing.List[CameraDetectionSchema]] = None

@strawberry.type
class DetectionNestedStaff(StaffSchema):
    detection: Optional[typing.List[DetectionSchema]] = None
@strawberry.type
class CameraReport(CameraSchema):
    staff: Optional[DetectionNestedStaff] = None
    # detection: Optional[typing.List[DetectionSchema]] = None

""" Return Type Class"""
@strawberry.type
class CommonReportReturn:
    staff: typing.List[CommonReport]
    meta: Optional[MetaData]
    
@strawberry.type
class StaffReportReturn:
    staff: typing.List[StaffReport]
    meta: Optional[MetaData]
    
@strawberry.type
class CameraReportReturn:
    camera: typing.List[CameraReport]
    meta: Optional[MetaData]
    
""" Input Params"""
@strawberry.input
class DateRange:
    start_date: str
    end_date: str
    
@strawberry.input
class TimeRange:
    start_time: str
    end_time: Optional[str] = None
@strawberry.input
class QueryParams:
    staff_id : Optional[int] = None
    staff_code : Optional[str] = None
    email_code : Optional[str] = None
    state: Optional[int] = None
    camera_id: Optional[int] = None
    camera_ip: Optional[str] = None
    staff_name: Optional[str] = None
    sorted: Optional[str] = None
    search: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    staff_limit: Optional[int] = None
    staff_offset: Optional[int] = None
    detection_limit: Optional[int] = None
    detection_offset: Optional[int] = None
    detection_sort: Optional[str] = None
    
@strawberry.input
class CommonReportParams:
    staff_code : Optional[str] = None
    email_code : Optional[str] = None
    state : Optional[int] = None
    sort : Optional[str] = None
    limit : Optional[int] = None
    offset : Optional[int] = None
@strawberry.input
class StaffReportParams:
    time_range: TimeRange
    staff_id : Optional[int] = None
    staff_code : Optional[str] = None
    staff_sort: Optional[str] = None
    search: Optional[str] = None
    detection_limit: Optional[int] = None
    detection_offset: Optional[int] = None
    detection_sort: Optional[str] = None
    
@strawberry.input
class CameraReportParams:
    time_range: TimeRange
    staff_id : Optional[int] = None
    staff_code : Optional[str] = None
    email_code : Optional[str] = None
    state: Optional[int] = None
    camera_id: Optional[int] = None
    camera_ip: Optional[str] = None
    staff_name: Optional[str] = None
    sorted: Optional[str] = None
    search: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    staff_limit: Optional[int] = None
    staff_offset: Optional[int] = None
    detection_limit: Optional[int] = None
    detection_offset: Optional[int] = None
    detection_sort: Optional[str] = None