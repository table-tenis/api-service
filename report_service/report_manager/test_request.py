from distutils.dir_util import copy_tree
from operator import or_
import requests
from json import loads
from io import StringIO
import pandas as pd
from sqlalchemy import create_engine, select, and_, or_, not_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import threading
from core import helper
# defined a URL variable that we will be
# using to send GET or POST requests to the API
POSTGRES_HOST = "172.21.100.15"
POSTGRES_PORT = 5432
POSTGRES_DB = "faceid_clone"
POSTGRES_URL = f"postgresql+pg8000://postgres:postgres@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
print("DATABASE_URL = ", POSTGRES_URL)
engine = create_engine(POSTGRES_URL, echo=True)
BASE = declarative_base(engine)

def get_session():
    with Session(engine) as session:
        yield session
        session.close()
class Detection(BASE):
    __tablename__ = 'detection'
    __table_args__ = {'autoload': True}
    
class Staff(BASE):
    __tablename__ = 'staff'
    __table_args__ = {'autoload': True}
    
class Camera(BASE):
    __tablename__ = 'camera'
    __table_args__ = {'autoload': True}      
  
url = "http://0.0.0.0:9032/graphql/"
cam_url = 'http://172.21.100.167:8888/api/xface/v1/cameras/profiles'
discovery_url = 'http://172.21.100.167:8888/api/xface/v1/cameras/discovery/reliable'
 
body = """
{
  getReport(queryParams:{emailCode:"tainp"}){
    staffCode,
    emailCode,
    fullname,
    dateOfBirth,
    report{
      checkin,
      checkout,
      reportDate
    }
  }
}
"""

query_string = """
    query getUser($id: ID) {
        me(id: $id) {
            id
            name
        }
    }
 """
# variables = {"id": 12}
# response = requests.get(url=url, json=body)
# print("response status code: ", response.status_code)
# if response.status_code == 200:
#   print(response.content)
  
#   s=str(response.content,'utf-8')

#   data = StringIO(s) 

#   df=pd.read_csv(data)
#   df.to_csv("report_tmp.csv")
  # data = loads(response.content)
  # print(data)
  # for key, value in data.items():
  #   print(key)
  # print(data['getReport'])
  # print(response.headers['X-Process-Time'])
auth = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJvb3QiLCJhdXRob3JpemF0aW9uIjoie1wiaXNfcm9vdFwiOiB0cnVlfSIsImV4cGlyZXMiOjE2NjcyMTI4MTMuNTE3NTcxfQ.u7-SO_zmpu1zLJAOdzdmb48xskSUf04kTNgEJQmpM3Q"
# ips = []
# for session in get_session():
#     statement = select(Camera)
#     data = session.execute(statement).all()
#     for dat in data:
#       ips.append(dat[0].ip)
#       # print(dat[0].ip)

# for session in get_session():
#   for ip in ips:
#     camera = session.execute(select(Camera).where(Camera.ip == ip)).all()
#     response = requests.get(url=cam_url, params={"user":"admin", "password":"123456a@", "ip":ip}, headers={'Authorization': auth})
#     profile = loads(response.content)
#     print(profile, type(profile))
#     if profile == "unreachable":
#       continue
#     if profile.get('rtsp_uri') == None or profile.get('stream') == None:
#       continue
#     for cam in camera:
#       cam = cam[0]
#       setattr(cam, "rtsp_uri", profile['rtsp_uri'])
#       setattr(cam, "stream", profile['stream'])
#       session.add(cam)
#       session.commit()
#       session.refresh(cam)


# ip_discovery = []
# def  discovery(ip_list):
#   global ip_discovery
#   for ip in ip_list:
#     response = requests.get(url=discovery_url, params={"ip":ip}, headers={'Authorization': auth})
#     res = loads(response.content)
#     if len(res) > 0:
#       ip_discovery.append(res[0])

# ip_list = []
# for i in range(100, 120):
#   ip = '172.21.120.' + str(i)
#   ip_list.append(ip)

# print("ip list = ", ip_list)
# THREAD_SIZE = 16
# thread_list = []
# step_size = int(len(ip_list)/THREAD_SIZE)
# redundance = len(ip_list) % THREAD_SIZE
# if len(ip_list) <= THREAD_SIZE:
#   for ip in ip_list:
#     thread_list.append(threading.Thread(target=discovery, args=([ip],)))
# else:
#   for i in range(THREAD_SIZE):
#     if i < THREAD_SIZE - 1:
#       thread_list.append(threading.Thread(target=discovery, args=(ip_list[i*step_size:(i+1)*step_size],)))
#     else:
#       thread_list.append(threading.Thread(target=discovery, args=(ip_list[i*step_size:],)))
      
  
# for t in thread_list:
#   t.start()
  
# for t in thread_list:
#   t.join()

# print("ip discovery = ", ip_discovery)

# statement = select(Detection).options('staff_id').where(Detection.camera_id == 104).group_by("staff_id")
class Box:
    def __init__(self, x, y, w, h) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
box = Box(0,1000, 3840, 1160)
for session in get_session():
  result = session.query(Detection.staff_id).where(Detection.camera_id == 104).\
                  where(and_(Detection.detection_time >= helper.str_to_date("2022-08-16"), Detection.detection_time <= helper.str_to_date("2022-08-17"))).\
                    where(not_(or_(or_(Detection.bbox_x1+Detection.bbox_w < box.x, box.x+box.w < Detection.bbox_x1 ), 
                                                    or_(Detection.bbox_y1+Detection.bbox_h < box.y, box.y+box.h < Detection.bbox_y1)))).\
                                                      group_by(Detection.staff_id).all()
  statement = select(Detection.staff_id).group_by(Detection.staff_id)
  ress = session.execute(statement).all()
  for res in ress:
    print(res[0])
  # print("result = ", result)
  # staff_id = [res[0] for res in result]
  # statement = select(Staff).where(Staff.id.in_(staff_id))
  # staffs = session.execute(statement).all()
  # for staff in staffs:
  #   staff = staff[0]
  #   print(staff.id, staff.staff_code, staff.mail_code, staff.full_name)