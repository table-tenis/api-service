import sqlalchemy
from sqlalchemy import create_engine, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from json import dumps, loads
import pymysql.cursors
import pandas as pd
from datetime import datetime, date
from core import helper

engine = create_engine("mariadb+mariadbconnector://root:root@172.21.100.167:3306/xface_system", echo=True)

mariadb_config = {
    'host': '172.21.100.167',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'xface_system'
}

Base = declarative_base(engine)
class Detection(Base):
    __tablename__ = 'detection'
    __table_args__ = {'autoload': True}
    
class Mot(Base):
    __tablename__ = 'mot'
    __table_args__ = {'autoload': True}
    
class Staff(Base):
    __tablename__ = 'staff'
    __table_args__ = {'autoload': True}
    
class Camera_Test(Base):
    __tablename__ = 'camera_test'
    __table_args__ = {'autoload': True}

camera = Camera_Test()

profile = {'rtsp_uri': ['rtsp://172.21.111.104:554/main', 'rtsp://172.21.111.104:554/sub'], 
           'stream': ['encoding/H264/width/3840/height/2160/framerate_limit/15/bitrate_limit/3072', 'encoding/H264/width/640/height/480/framerate_limit/25/bitrate_limit/512']}
setattr(camera, 'ip', '172.21.104.100')
setattr(camera, 'name', 'Cam tang 10')
setattr(camera, 'description', 'floor 10')
setattr(camera, 'profiles', dumps(profile))

# with Session(engine) as session:
#         # session.add(camera)
#         # session.commit()
        
#         cam = session.execute(select(Camera_Test)).first()
#         print(cam[0].profiles, type(cam[0].profiles))
#         data = loads(cam[0].profiles)
#         print(data['rtsp_uri'], type(data['rtsp_uri']))
        
try:
    conn = pymysql.connect(**mariadb_config)
except Exception as e:
    print(e)
with conn.cursor() as cursor:
    start_time = "2022-10-17"
    end_time = "2022-10-19"
    report_date = "2022-10-20"
    statememt = f"""select r.staff_id, r.checkin, r.checkout from (select @start_time:="{start_time}" p1) param1, 
                    (select @end_time:="{end_time}" p2) param2, aggregate_report as r limit 10;"""
    
    print(report_date, helper.date_to_str(date.today()), report_date == helper.date_to_str(date.today()))
    if(report_date == helper.date_to_str(date.today())):
        statememt = """select r.staff_code, r.fullname, r.unit, r.title, r.checkin, r.checkout, current_date 
                        from (select @start_time:=curdate() p1) param1, 
                             (select @end_time:=(current_date + interval '23:50' hour_minute) p2) param2, 
                             aggregate_report as r;"""
    else:
        statememt = f"""select s.staff_code, s.fullname, r.checkin, r.checkout, r.report_date 
                        from staff as s left outer join 
                        (select staff_id, checkin, checkout, report_date from report where report_date = '{report_date}') as r 
                        on s.id = r.staff_id 
                        where s.state != 0;"""
    # statememt = """select id, staff_id, detection_time from detection_tmp where id >= 642394;"""
    # today = date.today()
    # print(today, type(today), helper.date_to_str(today) == report_date)
    print(statememt)
    cursor.execute(statememt)
    result = cursor.fetchall()
    print(len(result))
    list_data = []
    for res in result:
        list_data.append({'staff_code':res[0], 'fullname':res[1], 'checkin':res[2], 'checkout':res[3], 'report_date':res[4]})
        # list_data.append({'id':res[0], 'staff_id':res[1], 'detection_time':res[2]})
    df = pd.DataFrame(list_data)
    df.to_csv('report.csv')