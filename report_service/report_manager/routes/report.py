from time import time

from fastapi import APIRouter, HTTPException, status, Depends, Security, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from priority import DeadlockError
from sqlmodel import Session, select, and_, or_, not_
from sqlalchemy.orm import load_only
from dependencies import CommonQueryParams, Authorization
from core.database import get_session, engine, db, get_cursor, mongodb
from core.tag_qualifier_tree import Tree, verify_query_params, print_subtree, gender_query
from core.helper import datetime_to_str
import pandas as pd
from datetime import datetime

from core import helper
report_router = APIRouter(tags=["Report"])

# def site_labeling_tree(tree):
#     if tree.key[0] == -1:
#         tree.name = 'root'
#     elif tree.key[0] == 0:
#         tree.name = 'site.id = '
#     for child in tree.children:
#         site_labeling_tree(child)
        
# def site_tree_to_query(tree_list):
#     root = Tree((-1,-1,-1,-1))
#     root.name = 'root'
#     for tree in tree_list:
#         root.add_child(tree)
#     site_labeling_tree(root)
#     # print_subtree(root)
#     return gender_query(root)

""" Get reports """
@report_router.get("/bytime")
def report_bytime(start_time:str = Query(default=None), 
                  end_time:str = Query(default=None), 
                  limit: int = Query(default=None, gt=0),
                  sort: str = Query(default=None, regex="^[+-](fullname|staff_code)"),
                  cursor = Depends(get_cursor)):
    
    limit_param = ""
    sort_param = ""
    if limit != None:
        limit_param += f"limit {limit}"
    if sort != None:
        if sort[0] == "+":
            sort_param += f"order by staff.{sort[1:]}"
        else:
            sort_param += f"order by staff.{sort[1:]} desc"
    
    if start_time == None:
        start_time = helper.datetime_to_str(datetime.now())   
    if end_time == None:
        end_time = helper.datetime_to_str(datetime.now())
        
    three_days_before = datetime.fromtimestamp(time() - 3*24*3600)
    result = []
    if start_time > helper.datetime_to_str(three_days_before):
        # Get Info From Mongodb
        print("Get mongodb data")
        result = mongodb.checkin_checkout_sumary(start_time=start_time, end_time=end_time)
             
    statement = f"select staff.staff_code, staff.email_code, staff.fullname, staff.unit, staff.title, b.min_time, b.max_time "\
                    "from staff left outer join (select staff_id, Min(detection_time) as min_time, Max(detection_time) as max_time "\
                                                "from detection "\
                                                "where (detection_time >= '{}') and (detection_time <= '{}') "\
                                                "group by staff_id) as b "\
                    "on staff.id = b.staff_id "\
                    "where staff.state != 0 {} {};".format(start_time, end_time, sort_param, limit_param)
    print("statement = ", statement)
    # return mongodb.checkin_checkout_sumary(start_time="2022-10-14")
    cursor.execute(statement)
    staffs = cursor.fetchall()
    list_data = []
    for staff in staffs:
        # print(staffs, type(staffs))
        list_data.append({'staff_code':staff[0], 'email_code':staff[1], 'fullname':staff[2], 'unit':staff[3], 
                          'title': staff[4], 'checkin':datetime_to_str(staff[5]), 'checkout':datetime_to_str(staff[6])})
    result = list_data
    df = pd.DataFrame(result)
    df.to_csv('data/report_bytime.csv')
    try:
        res = FileResponse("data/report_bytime.csv", filename='report.csv')
    except Exception as e:
        return str(e)
    return res

@report_router.get("/person")
def report_detect_per_person(staff_id: int = Query(default=None), staff_code: str = Query(default=None),
                             staff_name: str = Query(default=None), start_time:str = Query(default=None), 
                             end_time:str = Query(default=None), limit: int = Query(default=None, gt=0),
                             sorted: str = Query(default=None, regex="^[+-](detection_time)"),
                             cursor = Depends(get_cursor)):
    
    
    staff_id_param, staff_code_param, staff_name_param, limit_param, sort_param = "", "", "", "", ""
    # staff_id, staff_code, fullname search
    if staff_id != None:
        staff_id_param = f"and staff_id = {staff_id}"
    if staff_code != None:
        staff_code_param = f"and staff_code = {staff_code}"
    if staff_name != None:
        staff_name_param = f"""and fullname like '%{staff_name}%'"""
         
    # sorted, limit params
    if limit != None:
        limit_param += f"limit {limit}"
    if sorted != None:
        if sorted[0] == "+":
            sort_param += f"order by detection.{sorted[1:]}"
        else:
            sort_param += f"order by detection.{sorted[1:]} desc"
    
    if start_time == None:
        start_time = helper.datetime_to_str(datetime.now())   
    if end_time == None:
        end_time = helper.datetime_to_str(datetime.now()) 
    
    s = f"select staff.staff_code, staff.email_code, staff.fullname, staff.unit, detection.detection_time "\
        "from staff left outer join detection on staff.id = detection.staff_id "\
            "where (detection_time >= '{}' and detection_time <= '{}') "\
                "{} {} {} {} {};".format(start_time, end_time, staff_id_param, staff_code_param, 
                                         staff_name_param, sort_param, limit_param)       
    statement = f"select staff.staff_code, staff.email_code, staff.fullname, staff.unit, b.min_time, b.max_time "\
                    "from staff left outer join (select staff_id, Min(detection_time) as min_time, Max(detection_time) as max_time "\
                                                "from detection "\
                                                "where (detection_time >= '{}') and (detection_time <= '{}') "\
                                                "group by staff_id) as b "\
                    "on staff.id = b.staff_id "\
                    "where staff.state != 0 {} {};".format(start_time, end_time, sort_param, limit_param)
    print("statement = ", s)
    cursor.execute(s)
    staffs = cursor.fetchall()
    return staffs
    list_data = []
    for staff in staffs:
        # print(staffs, type(staffs))
        list_data.append({'staff_code':staff[0], 'mail_code':staff[1], 'fullname':staff[2], 'unit':staff[3], 
                          'checkin':datetime_to_str(staff[4]), 'checkout':datetime_to_str(staff[5])})
    return list_data