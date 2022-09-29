from time import time

from fastapi import APIRouter, HTTPException, status, Depends, Security, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel import Session, select, and_, or_, not_
from sqlalchemy.orm import load_only
from dependencies import CommonQueryParams, Authorization
from core.database import redis_db, get_session, engine, db, get_cursor
from core.tag_qualifier_tree import Tree, verify_query_params, print_subtree, gender_query
from core.helper import datetime_to_str
report_router = APIRouter(tags=["Report"])

def site_labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'site.id = '
    for child in tree.children:
        site_labeling_tree(child)
        
def site_tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    site_labeling_tree(root)
    # print_subtree(root)
    return gender_query(root)           

""" Get reports """
@report_router.get("/bytime")
def report_bytime(start_time:str, end_time:str, limit: int = Query(default=None, gt=0),
                        sort: str = Query(default=None, regex="^[+-](fullname|staff_code)"),
                        cursor = Depends(get_cursor)):
    # conn = mariadb.connect(**config)
    # cur = conn.cursor()
    start_t = start_time
    end_t = end_time
    limit_param = ""
    sort_param = ""
    if limit != None:
        limit_param += f"limit {limit}"
    if sort != None:
        if sort[0] == "+":
            sort_param += f"order by staff.{sort[1:]}"
        else:
            sort_param += f"order by staff.{sort[1:]} desc"
            
    statement = f"select staff.staff_code, staff.email_code, staff.fullname, staff.unit, b.min_time, b.max_time "\
                    "from staff left outer join (select staff_id, Min(detection_time) as min_time, Max(detection_time) as max_time "\
                                                "from detection "\
                                                "where (detection_time >= '{}') and (detection_time <= '{}') "\
                                                "group by staff_id) as b "\
                    "on staff.id = b.staff_id "\
                    "where staff.state != 0 {} {};".format(start_time, end_time, sort_param, limit_param)
    print("statement = ", statement)
    cursor.execute(statement)
    staffs = cursor.fetchall()
    list_data = []
    for staff in staffs:
        # print(staffs, type(staffs))
        list_data.append({'staff_code':staff[0], 'mail_code':staff[1], 'fullname':staff[2], 'unit':staff[3], 
                          'checkin':datetime_to_str(staff[4]), 'checkout':datetime_to_str(staff[5])})
    return list_data