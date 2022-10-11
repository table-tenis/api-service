from time import time

from fastapi import APIRouter, HTTPException, status, Depends, Security, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel import Session, select, and_, or_, not_
from sqlalchemy.orm import load_only

from models import Staff, StaffBase
from schemas import StaffUpdate, CameraUpdate
from dependencies import CommonQueryParams, Authorization
from core.database import get_session, engine, db, get_cursor
from core.tag_qualifier_tree import Tree, verify_query_params, print_subtree, gender_query
staff_router = APIRouter(tags=["Staff"])

# Labeling to tree nodes for assign condition query
def staff_labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'staff.id = '
    for child in tree.children:
        staff_labeling_tree(child)

# Staff trees to condition query      
def staff_tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    staff_labeling_tree(root)
    # print_subtree(root)
    return gender_query(root)           

""" Add new staff. """
@staff_router.post("/")
async def add_a_new_staff(staff: Staff, 
                         authorization: Authorization = Security(scopes=['staff', 'c']),
                         session = Depends(get_session)) -> dict:
    if staff.id != None:
        staff_exist = db.get_by_id(session, select(Staff).where(Staff.id == staff.id))
        if staff_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff Supplied Id Is Existed."
            )
    staff = db.add(session, staff)
    return {
        "Response": "New Staff Successfully Registered!",
        "Id": staff.id
    }

""" Get staffs. """
@staff_router.get("/")
async def get_staffs(id: int = Query(default=None), 
                    staff_code: str = Query(default=None),
                    email_code: str = Query(default=None),
                    search: str = Query(default=None, regex="(id|staff_code|email_code|unit|title|fullname)-"),
                    sorted: str = Query(default=None, regex="^[+-](id|staff_code|email_code|unit|title|fullname)"),
                    limit: int = Query(default=None, gt=0),
                    authorization: Authorization = Security(scopes=['staff', 'r']),
                    cursor = Depends(get_cursor)):
    # This Block Verify Query Params With Tag Qualifier Authorizarion Tree.
    # If Size Of Matched Trees List Is 0, Query Params List Don't Match Any Tag Qualifier Authorization.
    # Else, We Have Matched_Trees. And Decorate Staetment With Matched_Tree.
    matched_trees = verify_query_params([id], authorization.key)
    if len(matched_trees) == 0:
        return []
    filter_id_param = staff_tree_to_query(matched_trees)

    limit_param, search_param, sort_param, staff_code_param, email_code_param = "", "", "", "", ""
    
    # Add limit query
    if limit != None and limit != "":
        limit_param += f"limit {limit}"
    # Add search query
    if search != None:
        search = search.split('-')
        if search[1] != '':
            search_param += f"staff.{search[0]} like '%{search[1]}%'"
        print('search param = ', search_param)
    # Add order by query
    if sorted != None:
        if sorted[0] == "+":
            sort_param += f"order by staff.{sorted[1:]}"
        else:
            sort_param += f"order by staff.{sorted[1:]} desc"
    if staff_code != None:
        staff_code_param += f"staff.staff_code = '{staff_code}'"
    if email_code != None:
        email_code_param += f"staff.email_code = '{email_code}'"
    
    # Complete condition statement
    condition_statement = ""
    conditions_list = [filter_id_param, staff_code_param, email_code_param, search_param]
    first_add = False
    for condition in conditions_list:
        if condition != '':
            if not first_add:
                condition_statement = 'where ' + condition
                first_add = True
            else:
                condition_statement += ' and ' + condition
    print(condition_statement)
    statement = f"select staff.id, staff.staff_code, staff.email_code, "\
                    "staff.unit, staff.title, staff.fullname, staff.nickname, staff.cellphone, "\
                    "staff.date_of_birth, staff.sex, staff.state, staff.notify_enable, staff.note "\
                    "from staff "\
                    "{} {} {};"\
                    .format(condition_statement, sort_param, limit_param)
    print("statement = ", statement)
    try:
        cursor.execute(statement)
        staffs = cursor.fetchall()
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = str(e)
            )
    list_site = [{'id':staff[0], 'staff_code':staff[1], 'email_code':staff[2], 
                  'unit': staff[3], 'title': staff[4], 'fullname': staff[5], 
                  'nickname': staff[6], 'cellphone': staff[7], 'date_of_birth': staff[8], 
                  'sex': staff[9], 'state': staff[10], 'notify_enable': staff[11], 
                  'note': staff[12]} for staff in staffs]
    # print(list_camera)
    return JSONResponse(content=jsonable_encoder(list_site))



""" Update staff info""" 
@staff_router.put("/")
async def update_site_info(body: StaffBase, 
                            id: int = Query(), 
                            authorization: Authorization = Security(scopes=['staff', 'u']),
                            session = Depends(get_session)):
    staff = db.get_by_id(session, select(Staff).where(Staff.id == id))
    if staff:
        matched_trees = verify_query_params([id], authorization.key)
        if len(matched_trees) == 0:
            return {"Response" : "Permission Denied!"}
        
        staff_data = body.dict(exclude_unset=True)
        for key, value in staff_data.items():
            setattr(staff, key, value)
            
        staff = db.add(session, staff)
        return staff
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Site Supplied Id Does Not Exist"
    )
    
""" Delete a staff. """
@staff_router.delete("/")
async def delete_a_site(id: int = Query(), 
                        authorization: Authorization = Security(scopes=['staff', 'd']),
                        session = Depends(get_session)):
    staff = db.get_by_id(session, select(Staff).where(Staff.id == id))
    if staff:
        matched_trees = verify_query_params([id], authorization.key)
        if len(matched_trees) == 0:
            return {"Response" : "Permission Denied!"}
        db.delete(session, staff)
        return {
            "Response": "Staff Deleted Successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Staff Does Not Exist"
    )