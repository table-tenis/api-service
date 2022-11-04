from fastapi import Query, Security, Request, HTTPException, status
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
from core import helper
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import column
from sqlmodel import select, and_, or_, not_, func
from core.database import get_session, engine, db, get_cursor
from models import Report, Staff, Detection, Camera
import strawberry
from strawberry.fastapi import GraphQLRouter
from json import dump, dumps
import time

from schemas import (
    DetectionNestedStaff,
    MetaData, 
    ReportSchema, 
    DetectionSchema,
    CameraDetectionSchema,
    CommonReport,
    StaffReport,
    CameraReport,
    CommonReportReturn,
    StaffReportReturn,
    CameraReportReturn,
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
    def common_report(self, params: CommonReportParams) -> CommonReportReturn:
        # session = get_session
        report_dict = {}
        statement = ""
        if params.date_range != None and params.report_date == None:
            statement = f"""select r.staff_id, r.checkin, r.checkout, r.report_date from report as r 
            where report_date >= '{params.date_range.start_date}' and report_date <= '{params.date_range.end_date}' ;"""
        else:
            if params.report_date == None or params.report_date < date.today():
                if params.report_date == None:
                    statement = """select r.staff_id, r.checkin, r.checkout, r.report_date from report as r ;"""
                else:
                    statement = f"""select r.staff_id, r.checkin, r.checkout, r.report_date from report as r where report_date = '{params.report_date}' ;"""
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
            limit = params.limit
            offset = params.offset
            statement = get_staff_where_statement(statement, params.staff_id, "id")
            statement = get_staff_where_statement(statement, params.staff_code, "staff_code")
            statement = get_staff_where_statement(statement, params.email_code, "email_code")
            statement = get_staff_where_statement(statement, params.state, "state")
            statement = get_staff_sort_statement(statement, params.sort)
                
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
            return CommonReportReturn(staff=[CommonReport(id=res[0].id, staff_code=res[0].staff_code, 
                                email_code=res[0].email_code, fullname=res[0].fullname, title=res[0].title, 
                                unit=res[0].unit, nickname=res[0].nickname, cellphone=res[0].cellphone,
                                date_of_birth=res[0].date_of_birth, sex=res[0].sex, state=res[0].state, 
                                notify_enable=res[0].notify_enable, note=res[0].note, 
                                report=report_dict.get(res[0].id)) for res in staffs],
                                meta=MetaData(limit=limit, offset=offset, size=size))
            
    @strawberry.field
    def staff_report(self, params: StaffReportParams) -> StaffReportReturn:
        start_time = params.time_range.start_time
        end_time = params.time_range.end_time
        if end_time == None:
            end_time = helper.datetime_to_str(datetime.now())
        detection_limit = params.detection_limit
        detection_offset = params.detection_offset
        for session in get_session():
            # Get Staff Records
            statement = select(Staff)
            statement = get_staff_where_statement(statement, params.staff_id, "id")
            statement = get_staff_where_statement(statement, params.staff_code, "staff_code")
            statement = get_staff_where_statement(statement, params.email_code, "email_code")
            statement = get_staff_where_statement(statement, params.staff_state, "state")
            statement = get_staff_search_statement(statement, params.staff_search)
            statement = get_staff_sort_statement(statement, params.staff_sort)
            if params.staff_limit != None and params.staff_limit > 0:
                statement = statement.limit(params.staff_limit)
            if params.staff_offset != None and params.staff_offset > 0:
                statement = statement.offset(params.staff_offset)
            staffs = db.get_all(session, statement)
            if not staffs:
                return StaffReportReturn(staff=[StaffReport()], 
                                            meta=MetaData(staff_limit=params.staff_limit, 
                                                          staff_offset=params.staff_offset,
                                                          detection_limit=params.detection_limit, 
                                                          detection_offset=params.detection_offset))
            # Get all camera instance
            statement = select(Camera)
            cameras = db.get_all(session, statement)
            camera_dict = {}
            for camera in cameras:
                camera_dict[camera[0].id] = camera[0]
            
            staff_list = []
            for staff in staffs:
                # Get detection information for staff
                staff= staff[0]
                statement = select(Detection)
                statement = statement.where(and_(Detection.detection_time >= start_time, Detection.detection_time <= end_time))
                statement = statement.where(Detection.staff_id == staff.id)
                statement = get_detection_sort_statement(statement, params.detection_sort)
                if detection_limit != None and detection_limit > 0:
                    statement = statement.limit(detection_limit)
                if detection_offset != None and detection_offset > 0:
                    statement = statement.offset(detection_offset)
                # Get all detection records 
                detections = db.get_all(session, statement)
                if not detections:
                    camera_detection_schema_list = None
                else:
                    camera_detection_schema_list = []
                    for detection in detections:
                        detection = detection[0]
                        camera = camera_dict[detection.cam_id]
                        camera_detection_schema_list.append(CameraDetectionSchema(id=camera.id, site_id=camera.site_id, 
                                                            ip=camera.ip, name=camera.name, description=camera.description, 
                                                            rtsp_uri=camera.rtsp_uri, stream=camera.stream,
                                                            session_id=detection.session_id, frame_id=detection.frame_id, 
                                                            detection_time=detection.detection_time, 
                                                            detection_score=detection.detection_score,
                                                            x=detection.box_x, y=detection.box_y, w=detection.box_width, 
                                                            h=detection.box_height, feature=detection.feature, 
                                                            uri_image=detection.uri_image, polygon_face=detection.polygon_face))
                     
                staff_list.append(StaffReport(id=staff.id, staff_code=staff.staff_code, email_code=staff.email_code,
                                            fullname=staff.fullname, title=staff.title, unit=staff.unit, 
                                            nickname=staff.nickname, cellphone=staff.cellphone, 
                                            date_of_birth=staff.date_of_birth, sex=staff.sex, state=staff.state, 
                                            notify_enable=staff.notify_enable, note=staff.note, 
                                            camera_detection=camera_detection_schema_list))
                
            return StaffReportReturn(staff=staff_list, 
                                     meta=MetaData(staff_limit=params.staff_limit, 
                                                staff_offset=params.staff_offset,
                                                detection_limit=params.detection_limit, 
                                                detection_offset=params.detection_offset))

    @strawberry.field
    def camera_report(self, params: CameraReportParams) -> CameraReportReturn:
        start_time = params.time_range.start_time
        end_time = params.time_range.end_time
        box = params.box
        if end_time == None:
            end_time = helper.datetime_to_str(datetime.now())
        staff_sort, staff_limit, staff_offset = params.staff_sort, params.staff_limit, params.staff_offset
        detection_sort, detection_limit, detection_offset = params.detection_sort, params.detection_limit, params.detection_offset
        for session in get_session():
            statement = select(Camera)
            statement = get_camera_where_statement(statement, params.camera_id, "id")
            statement = get_camera_where_statement(statement, params.camera_ip, "ip")
            statement = get_camera_search_statement(statement, params.camera_search)
            statement = get_camera_sort_statement(statement, params.camera_sort)
            if params.camera_limit != None and params.camera_limit > 0:
                statement = statement.limit(params.camera_limit)
            if params.camera_offset != None and params.camera_offset > 0:
                statement = statement.limit(params.camera_offset)
            cameras = db.get_all(session, statement)
            if not cameras:
                return CameraReportReturn(camera=[CameraReport()], 
                                          meta=MetaData(camera_limit=params.camera_limit, 
                                                        camera_offset=params.camera_offset))
            camera_report_list = []
            for camera in cameras:
                # Get detection information for staff
                camera= camera[0]
                # Query staff
                staffs = None
                if params.staff_id != None or \
                params.staff_code!= None or \
                params.email_code != None or \
                params.staff_state != None or \
                params.staff_search != None:
                    statement = select(Staff)
                    statement = get_staff_where_statement(statement, params.staff_id, "id")
                    statement = get_staff_where_statement(statement, params.staff_code, "staff_code")
                    statement = get_staff_where_statement(statement, params.email_code, "email_code")
                    statement = get_staff_where_statement(statement, params.staff_state, "state")
                    statement = get_staff_search_statement(statement, params.staff_search)
                    statement = get_staff_sort_statement(statement, staff_sort)
                    if staff_limit != None and staff_limit > 0:
                        statement = statement.limit(staff_limit)
                    if staff_offset != None and staff_offset > 0:
                        statement = statement.offset(staff_offset)
                    staffs = db.get_all(session, statement)
                    if not staffs:
                        camera_report_list.append(CameraReport(id=camera.id, site_id=camera.site_id, ip=camera.ip, 
                                                            name=camera.name, description=camera.description,
                                                                rtsp_uri=camera.rtsp_uri, stream=camera.stream))
                        continue
                
                statement = select(Detection)
                statement = statement.where(and_(Detection.detection_time >= start_time, 
                                                 Detection.detection_time <= end_time)).\
                                                        where(Detection.cam_id == camera.id)
                if staffs:
                    staff_id_list = []
                    for staff in staffs:
                        staff = staff[0]
                        staff_id_list.append(staff.id)
                    print("=======================> staff id list = ", staff_id_list)
                    statement = statement.where(Detection.staff_id.in_(staff_id_list))
                    statement = statement.with_hint(Detection, 'force index (FK_Detection_Staff)')
                else:
                    statement = statement.with_hint(Detection, 'force index (Time_Camid_Staffid)')
                if box != None:
                    polygon = f"POLYGON(({box.x} {box.y},{box.x+box.w} {box.y},{box.x+box.w} {box.y+box.h},{box.x} {box.y+box.h},{box.x} {box.y}))"
                    statement = statement.where(func.ST_Intersects(func.PolygonFromText(Detection.polygon_face), 
                                                                   func.PolygonFromText(polygon)))
                statement = get_detection_sort_statement(statement, detection_sort)
                
                start_time = time.time()
                detections = session.execute(statement).all()
                end_time = time.time()
                
                if not detections:
                    camera_report_list.append(CameraReport(id=camera.id, site_id=camera.site_id, ip=camera.ip, 
                                                           name=camera.name, description=camera.description,
                                                            rtsp_uri=camera.rtsp_uri, stream=camera.stream))
                    continue
                
                staff_list = []
                staff_schema_list = {}
                detection_schema_list = {}
                for detection in detections:
                    detection = detection[0]
                    if staff_schema_list.get(detection.staff_id) == None:
                        staff = session.execute(select(Staff).where(Staff.id == detection.staff_id)).all()
                        staff = staff[0][0]
                        staff_schema_list[staff.id] = staff
                    if detection_schema_list.get(detection.staff_id) == None:
                        detection_schema_list[detection.staff_id] = [DetectionSchema(session_id=detection.session_id,
                                                                    frame_id=detection.frame_id, 
                                                                    detection_time=detection.detection_time,
                                                                    detection_score=detection.detection_score, 
                                                                    x=detection.box_x, y=detection.box_y, 
                                                                    w=detection.box_width, h=detection.box_height,
                                                                    feature=detection.feature, uri_image=detection.uri_image,
                                                                    polygon_face=detection.polygon_face)]
                    else:
                        detection_schema_list[detection.staff_id].append(DetectionSchema(session_id=detection.session_id,
                                                                    frame_id=detection.frame_id, 
                                                                    detection_time=detection.detection_time,
                                                                    detection_score=detection.detection_score, 
                                                                    x=detection.box_x, y=detection.box_y, 
                                                                    w=detection.box_width, h=detection.box_height,
                                                                    feature=detection.feature, uri_image=detection.uri_image,
                                                                    polygon_face=detection.polygon_face))
                
                staff_limit_count = 0   
                staff_offset_count = 0
                staff_id_sorted = []
                if staff_sort != None and staff_sort == '-id':
                    staff_id_sorted = sorted(staff_schema_list.keys(), reverse=True)
                else:
                    staff_id_sorted = sorted(staff_schema_list.keys())
                for staff_id in staff_id_sorted:
                    staff = staff_schema_list[staff_id]
                    if staff_offset != None and staff_offset > 0 and staff_offset_count < staff_offset:
                        staff_offset_count += 1
                        continue
                    if detection_limit != None and detection_limit > 0:
                        if detection_offset != None and detection_offset > 0:
                            detection_schema_list[staff_id] = detection_schema_list[staff_id][detection_offset:detection_limit]
                        else:
                            detection_schema_list[staff_id] = detection_schema_list[staff_id][0:detection_limit]
                    staff_list.append(DetectionNestedStaff(id=staff.id, staff_code=staff.staff_code, 
                                                    email_code=staff.email_code, fullname=staff.fullname, 
                                                    title=staff.title, unit=staff.unit,
                                                    nickname=staff.nickname, cellphone=staff.cellphone,
                                                    date_of_birth=staff.date_of_birth, sex=staff.sex,
                                                    notify_enable=staff.notify_enable, note=staff.note,
                                                    detection=detection_schema_list[staff_id]))
                    staff_limit_count += 1
                    if staff_limit != None and staff_limit_count >= staff_limit:
                        break
                camera_report_list.append(CameraReport(id=camera.id, site_id=camera.site_id, ip=camera.ip, 
                                                    name=camera.name, description=camera.description,
                                                    rtsp_uri=camera.rtsp_uri, stream=camera.stream,
                                                    staff_list=staff_list))
                print("========================> staff id list = ", staff_id_sorted, " - len = ", len(staff_id_sorted))
                print("========================> detection statement = ", statement)
                print("========================> detection size = ", len(detections))
                print("========================> execute time = ", end_time-start_time)
            return CameraReportReturn(camera=camera_report_list, 
                                      meta=MetaData(camera_limit=params.camera_limit, 
                                                    camera_offset=params.camera_offset,
                                                    staff_limit=staff_limit,
                                                    staff_offset=staff_offset,
                                                    detection_limit=detection_limit,
                                                    detection_offset=detection_offset))
        
schema = strawberry.Schema(GraphQLQuery)
graphql_app = GraphQLRouter(schema)

""" Downloads common reports """
@graphql_app.get("/common-report/downloads")
async def common_report(request: Request):
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
    data = data.get("commonReport")
    if data == None:
        return []
    staffs = data.get("staff")
    if staffs == None:
        return []
    converted_data = []
    for staff in staffs:
        row_data = []
        for key, val in staff.items():
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
    for key, val in staffs[0].items():
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

""" Downloads staff reports """
@graphql_app.get("/staff-report/downloads")
async def staff_report(request: Request):
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
    data = data.get("staffReport")
    if data == None:
        return []
    staffs = data.get("staff")
    if staffs == None:
        return []
    with open("data/staff-report.json", "w") as outfile:
        dump(staffs, outfile)
    res = FileResponse("data/staff-report.json", filename='staff-report.json')
    return res

""" Downloads staff reports """
@graphql_app.get("/camera-report/downloads")
async def camera_report(request: Request):
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
    data = data.get("cameraReport")
    if data == None:
        return []
    cameras = data.get("camera")
    if cameras == None:
        return []
    with open("data/camera-report.json", "w") as outfile:
        dump(cameras, outfile)
    res = FileResponse("data/camera-report.json", filename='camera-report.json')
    return res