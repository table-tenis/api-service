from fastapi import Query, Security, Request, HTTPException, status
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
from core import helper
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import column
from sqlmodel import select, and_, or_, not_
from core.database import get_session, engine, db, get_cursor
from models import Report, Staff, Detection, Camera
import strawberry
from strawberry.fastapi import GraphQLRouter

from schemas import (
    DetectionNestedStaff,
    MetaData, 
    ReportSchema, 
    StaffSchema, 
    CameraSchema, 
    DetectionSchema,
    CameraDetectionSchema,
    CommonReport,
    StaffReport,
    CameraReport,
    CommonReportReturn,
    StaffReportReturn,
    CameraReportReturn,
    DateRange,
    TimeRange,
    QueryParams,
    CommonReportParams,
    StaffReportParams,
    CameraReportParams
)

def get_staff_sort_statement(statement, sort):
    if sort != None:
        if sort[0] == "-":
            if sort[1:] == 'staff_code':
                statement = statement.order_by(Staff.staff_code.desc())
            elif sort[1:] == 'fullname':
                statement = statement.order_by(Staff.fullname.desc())
            elif sort[1:] == 'email_code':
                statement = statement.order_by(Staff.email_code.desc())
            elif sort[1:] == 'unit':
                statement = statement.order_by(Staff.unit.desc())
            elif sort[1:] == 'title':
                statement = statement.order_by(Staff.title.desc())
            elif sort[1:] == 'date_of_birth':
                statement = statement.order_by(Staff.date_of_birth.desc())
        elif sort[0] == "+":
            if sort[1:] == 'staff_code':
                statement = statement.order_by(Staff.staff_code.asc())
            elif sort[1:] == 'fullname':
                statement = statement.order_by(Staff.fullname.asc())
            elif sort[1:] == 'email_code':
                statement = statement.order_by(Staff.email_code.asc())
            elif sort[1:] == 'unit':
                statement = statement.order_by(Staff.unit.asc())
            elif sort[1:] == 'title':
                statement = statement.order_by(Staff.title.asc())
            elif sort[1:] == 'date_of_birth':
                statement = statement.order_by(Staff.date_of_birth.asc())  
    return statement

def get_staff_where_statement(statement, param, attr:str):
    if param != None:
        if attr == "id":
            statement = statement.where(Staff.id == param)
        elif attr == "staff_code":
            statement = statement.where(Staff.staff_code == param)
        elif attr == "email_code":
            statement = statement.where(Staff.email_code == param)
        elif attr == "state":
            statement = statement.where(Staff.state == param)
    return statement
def get_staff_search_statement(statement, search):
    if search != None:
        search = search.split('-')
        if search[0] == 'fullname' and search[1] != '':
            statement = statement.filter(Staff.fullname.contains(search[1]))
        elif search[0] == 'staff_code' and search[1] != '':
            statement = statement.filter(Staff.staff_code.contains(search[1]))
        elif search[0] == 'email_code' and search[1] != '':
            statement = statement.filter(Staff.email_code.contains(search[1]))
        elif search[0] == 'unit' and search[1] != '':
            statement = statement.filter(Staff.unit.contains(search[1]))
        elif search[0] == 'title' and search[1] != '':
            statement = statement.filter(Staff.title.contains(search[1]))
        elif search[0] == 'nickname' and search[1] != '':
            statement = statement.filter(Staff.nickname.contains(search[1]))
    return statement

def get_camera_sort_statement(statement, sort):
    if sort != None:
        if sort[0] == "-":
            if sort[1:] == 'id':
                statement = statement.order_by(Camera.id.desc())
            elif sort[1:] == 'ip':
                statement = statement.order_by(Camera.ip.desc())
            elif sort[1:] == 'name':
                statement = statement.order_by(Camera.name.desc())
        elif sort[0] == "+":
            if sort[1:] == 'id':
                statement = statement.order_by(Camera.id.asc())
            elif sort[1:] == 'ip':
                statement = statement.order_by(Camera.ip.asc())
            elif sort[1:] == 'name':
                statement = statement.order_by(Camera.name.asc())
    return statement

def get_camera_where_statement(statement, param, attr:str):
    if param != None:
        if attr == "id":
            statement = statement.where(Camera.id == param)
        elif attr == "ip":
            statement = statement.where(Camera.ip == param)
    return statement
def get_camera_search_statement(statement, search):
    if search != None:
        search = search.split('-')
        if search[0] == 'description' and search[1] != '':
            statement = statement.filter(Camera.description.contains(search[1]))
        elif search[0] == 'name' and search[1] != '':
            statement = statement.filter(Camera.name.contains(search[1]))
    return statement

def get_detection_sort_statement(statement, sort):
    if sort != None:
        if sort[0] == "-":
            if sort[1:] == 'frame_id':
                statement = statement.order_by(Detection.frame_id.desc())
            elif sort[1:] == 'detection_time':
                statement = statement.order_by(Detection.detection_time.desc())
            elif sort[1:] == 'detection_score':
                statement = statement.order_by(Detection.detection_score.desc())
        elif sort[0] == "+":
            if sort[1:] == 'frame_id':
                statement = statement.order_by(Detection.frame_id.asc())
            elif sort[1:] == 'detection_time':
                statement = statement.order_by(Detection.detection_time.asc())
            elif sort[1:] == 'detection_score':
                statement = statement.order_by(Detection.detection_score.asc())
    return statement

def get_detection_where_statement(statement, param, attr:str):
    if param != None:
        if attr == "staff_id":
            statement = statement.where(Detection.staff_id == param)
        elif attr == "cam_id":
            statement = statement.where(Detection.cam_id == param)
    return statement

@strawberry.type
class GraphQLQuery:
    @strawberry.field
    def common_report(self, report_date: Optional[date] = None, 
                   date_range: Optional[DateRange] = None,
                   query_params: Optional[CommonReportParams] = None) -> CommonReportReturn:
        # session = get_session
        report_dict = {}
        statement = ""
        if date_range != None and report_date == None:
            statement = f"""select r.staff_id, r.checkin, r.checkout, r.report_date from report as r 
            where report_date >= '{date_range.start_date}' and report_date <= '{date_range.end_date}' ;"""
        else:
            if report_date == None or report_date < date.today():
                if report_date == None:
                    statement = """select r.staff_id, r.checkin, r.checkout, r.report_date from report as r ;"""
                else:
                    statement = f"""select r.staff_id, r.checkin, r.checkout, r.report_date from report as r where report_date = '{report_date}' ;"""
            else:
                statement = """select r.staff_id, r.checkin, r.checkout, current_date 
                                    from (select @start_time:=curdate() p1) param1, 
                                    (select @end_time:=(current_date + interval '23:50' hour_minute) p2) param2, 
                                    aggregate_report as r ;"""
        for cursor in get_cursor():
            print("statement = ", statement)
            # Get report data
            try:
                cursor.execute(statement)
                report = cursor.fetchall()
            except Exception as e:
                session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail = e._message()
                )
            for res in report:
                if report_dict.get(res[0]) == None:
                    report_dict[res[0]] = [ReportSchema(id=None, staff_id=res[0], checkin=res[1], 
                                                                checkout=res[2], report_date=res[3])]
                else:
                    report_dict[res[0]].append(ReportSchema(id=None, staff_id=res[0], checkin=res[1], 
                                                                checkout=res[2], report_date=res[3]))
        for session in get_session():    
            # Get staff data
            statement = select(Staff)
            limit, offset = None, None
            if query_params != None:
                limit = query_params.limit
                offset = query_params.offset
            if query_params != None:
                statement = get_staff_where_statement(statement, query_params.staff_code, "staff_code")
                statement = get_staff_where_statement(statement, query_params.email_code, "email_code")
                statement = get_staff_where_statement(statement, query_params.state, "state")
                statement = get_staff_sort_statement(statement, query_params.sort)
                
            print("=======> staff statement = ", statement)
            size = len(db.get_all(session, statement))
            if limit != None and limit > 0:
                    statement = statement.limit(limit)
            if offset != None and offset > 0:
                statement = statement.offset(offset)
            staffs = db.get_all(session, statement)
            
            if not staffs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail = "Staff Not Found"
                )
            return CommonReportReturn(staff=[CommonReport(id=res[0].id, staff_code=res[0].staff_code, email_code=res[0].email_code, fullname=res[0].fullname, 
                                title=res[0].title, unit=res[0].unit, nickname=res[0].nickname, cellphone=res[0].cellphone,
                                date_of_birth=res[0].date_of_birth, sex=res[0].sex, state=res[0].state, notify_enable=res[0].notify_enable, 
                                note=res[0].note, report=report_dict.get(res[0].id)) for res in staffs],
                                meta=MetaData(limit=limit, offset=offset, size=size))
            
    @strawberry.field
    def staff_report(self, query_params: StaffReportParams) -> StaffReportReturn:
        start_time = query_params.time_range.start_time
        end_time = query_params.time_range.end_time
        if end_time == None:
            end_time = helper.datetime_to_str(datetime.now())
        detection_limit = query_params.detection_limit
        detection_offset = query_params.detection_offset
        for session in get_session():
            # Get Staff Records
            statement = select(Staff)
            statement = get_staff_where_statement(statement, query_params.staff_id, "id")
            statement = get_staff_where_statement(statement, query_params.staff_code, "staff_code")
            statement =get_staff_search_statement(statement, query_params.search)
            statement = get_staff_sort_statement(statement, query_params.staff_sort)
            staffs = db.get_all(session, statement)
            if not staffs:
                return StaffReportReturn(staff_detection=[StaffReport()], 
                                            meta=MetaData(limit=query_params.detection_limit, 
                                                          offset=query_params.detection_offset))
            # Get all camera instance
            statement = select(Camera)
            cameras = db.get_all(session, statement)
            camera_dict = {}
            for camera in cameras:
                camera_dict[camera[0].id] = camera[0]  
            
            result = []
            for staff in staffs:
                # Get detection information for staff
                staff= staff[0]
                statement = select(Detection)
                
                statement = statement.where(and_(Detection.detection_time >= start_time, Detection.detection_time <= end_time))
                statement = statement.where(Detection.staff_id == staff.id)
                statement = get_detection_sort_statement(statement, query_params.detection_sort)
                if detection_limit != None and detection_limit > 0:
                    statement = statement.limit(detection_limit)
                if detection_offset != None and detection_offset > 0:
                    statement = statement.offset(detection_offset)
                # Get all detection records 
                detections = db.get_all(session, statement)
                if not detections:
                    detection_schema_list = None
                    camera_schema_list = None
                    camera_detection_schema_list = None
                else:
                    detections = [detection[0] for detection in detections]
                    camera_detection_schema_list = []
                    for detection in detections:
                        camera = camera_dict[detection.cam_id]
                        camera_detection_schema_list.append(CameraDetectionSchema(id=camera.id, site_id=camera.site_id, ip=camera.ip, name=camera.name,
                                                           description=camera.description, rtsp_uri=camera.rtsp_uri, stream=camera.stream,
                                                           session_id=detection.session_id, frame_id=detection.frame_id, 
                                                detection_time=detection.detection_time, detection_score=detection.detection_score,
                                                x=detection.box_x, y=detection.box_y, w=detection.box_width, h=detection.box_height,
                                                feature=detection.feature, uri_image=detection.uri_image))
                     
                result.append(StaffReport(id=staff.id, staff_code=staff.staff_code, email_code=staff.email_code,
                                                   fullname=staff.fullname, title=staff.title, unit=staff.unit, nickname=staff.nickname,
                                                   cellphone=staff.cellphone, date_of_birth=staff.date_of_birth, sex=staff.sex,
                                                   state=staff.state, notify_enable=staff.notify_enable, note=staff.note,
                                                   camera_detection=camera_detection_schema_list))
                
            return StaffReportReturn(staff=result, meta=MetaData(limit=detection_limit, offset=detection_offset))

    @strawberry.field
    def camera_report(self, query_params: CameraReportParams) -> CameraReportReturn:
        staff_id = query_params.staff_id
        staff_code = query_params.staff_code
        search = query_params.search
        limit = query_params.limit
        sort = query_params.sorted
        offset = query_params.offset
        start_time = query_params.time_range.start_time
        end_time = query_params.time_range.end_time
        camera_id = query_params.camera_id
        camera_ip = query_params.camera_ip
        staff_name = query_params.staff_name
        staff_limit = query_params.staff_limit
        staff_offset = query_params.staff_offset
        detection_limit = query_params.detection_limit
        detection_offset = query_params.detection_offset
        for session in get_session():
            statement = select(Camera)
            statement = get_camera_where_statement(statement, camera_id, "id")
            statement = get_camera_where_statement(statement, camera_ip, "ip")
            statement = get_camera_search_statement(statement, search)
            statement = get_camera_sort_statement(statement, sort)
            cameras = db.get_all(session, statement)
            if not cameras:
                return CameraReportReturn(camera_detection=[CameraReport()], meta=MetaData(limit=limit, offset=offset))
            # Get all staff instance
            statement = select(Staff)
            statement = get_staff_where_statement(statement, staff_id, "id")
            statement = get_staff_where_statement(statement, staff_code, "staff_code")
            statement = get_staff_search_statement(statement, staff_name)
            if staff_limit != None and staff_limit > 0:
                statement = statement.limit(staff_limit)
            if staff_offset != None:
                statement = statement.offset(staff_offset)
            staffs = db.get_all(session, statement)
            if not staffs:
                return CameraReportReturn(camera_detection=[CameraReport(id=cam[0].id, site_id=cam[0].site_id,
                                                                               ip=cam[0].ip, name=cam[0].name, 
                                                                               description=cam[0].description,
                                                                               rtsp_uri=cam[0].rtsp_uri, 
                                                                               stream=cam[0].stream) for cam in cameras], 
                                             meta=MetaData(limit=limit, offset=offset))
            staff_dict = {}
            for staff in staffs:
                staff_dict[staff[0].id] = staff[0]
            result = []
            for camera in cameras:
                # Get detection information for staff
                camera= camera[0]
                for staff_id, staff in staff_dict.items():
                    statement = select(Detection)
                    if end_time == None:
                        end_time = helper.datetime_to_str(datetime.now())
                    statement = statement.where(and_(Detection.detection_time >= start_time, Detection.detection_time <= end_time))
                    statement = statement.where(Detection.cam_id == camera.id)
                    statement = statement.where(Detection.staff_id == staff_id)
                    statement = get_detection_sort_statement(statement, query_params.detection_sort)
                    if detection_limit != None and detection_limit > 0:
                        statement = statement.limit(detection_limit)
                    if detection_offset != None and detection_offset > 0:
                        statement = statement.offset(detection_offset)
                    detections = db.get_all(session, statement)
                    if not detections:
                        result.append(CameraReport(id=camera.id, site_id=camera.site_id, ip=camera.ip,
                                                  name=camera.name, description=camera.description, 
                                                  rtsp_uri=camera.rtsp_uri, stream=camera.stream,
                                                  staff=DetectionNestedStaff(id=staff.id, 
                                                    staff_code=staff.staff_code, email_code=staff.email_code,
                                                    fullname=staff.fullname, title=staff.title, unit=staff.unit,
                                                    nickname=staff.nickname, cellphone=staff.cellphone,
                                                    date_of_birth=staff.date_of_birth, sex=staff.sex,
                                                    notify_enable=staff.notify_enable, note=staff.note)))
                    else:    
                        detections = [detection[0] for detection in detections]
                        result.append(CameraReport(id=camera.id, site_id=camera.site_id, ip=camera.ip,
                                                    name=camera.name, description=camera.description, 
                                                    rtsp_uri=camera.rtsp_uri, stream=camera.stream,
                                                    staff=DetectionNestedStaff(id=staff.id, 
                                                        staff_code=staff.staff_code, email_code=staff.email_code,
                                                        fullname=staff.fullname, title=staff.title, unit=staff.unit,
                                                        nickname=staff.nickname, cellphone=staff.cellphone,
                                                        date_of_birth=staff.date_of_birth, sex=staff.sex,
                                                        notify_enable=staff.notify_enable, note=staff.note,
                                                        detection=[DetectionSchema(session_id=detection.session_id,
                                                        frame_id=detection.frame_id, detection_time=detection.detection_time,
                                                        detection_score=detection.detection_score, x=detection.box_x,
                                                        y=detection.box_y, w=detection.box_width, h=detection.box_height,
                                                        feature=detection.feature, uri_image=detection.uri_image) 
                                                        for detection in detections])))  
            return CameraReportReturn(camera=result, meta=MetaData(limit=limit, offset=offset))
        
schema = strawberry.Schema(GraphQLQuery)
graphql_app = GraphQLRouter(schema)

""" Get reports """
@graphql_app.get("/downloads")
async def report_bytime(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        return e
    query = body.get("query")
    if query == None:
        return []
    res = await graphql_app.execute(query, context=graphql_app.context_getter)
    data = res.data
    if data == None:
        return []
    data = data.get("getReport")
    if data == None:
        return []
    converted_data = []
    for dat in data:
        row_data = []
        for key, val in dat.items():
            if key == "report":
                for report in val:
                    for k, v in report.items():
                        if v == None:
                            row_data.append(np.nan)
                        else:
                            row_data.append(v)
            else:
                if val == None:
                    print("append nan")
                    row_data.append(np.nan)
                else:
                    row_data.append(val)
        converted_data.append(row_data)
    column_name = []
    for key, val in data[0].items():
        if key == "report":
            for report in val:
                for k, v in report.items():
                    column_name.append(k)
        else:
            column_name.append(key)
    print(converted_data)
    print(column_name)
    df = pd.DataFrame(converted_data, columns=column_name)
    df.to_csv("data/report.csv", na_rep='NULL', index=True)
    res = FileResponse("data/report.csv", filename='report.csv')
    return res