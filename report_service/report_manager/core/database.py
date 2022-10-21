from sqlmodel import SQLModel, create_engine
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import APIRouter, HTTPException, status
# import mariadb
import pymysql.cursors
from pymongo import MongoClient
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import settings
from core import helper
# Mongo database and collections
class MongoDatabase:
    def __init__(self) -> None:
        print("MONGODB_HOST = ", settings.MONGODB_HOST, ", MONGODB_PORT = ", settings.MONGODB_PORT)
        self.client = MongoClient(settings.MONGODB_HOST, settings.MONGODB_PORT)
        self.xface_db = self.client['xface']
        self.detection_coll = self.xface_db['detection']
        
    def checkin_checkout_sumary(self, start_time = None, end_time = None):
        start_time = helper.strtime_to_utc(start_time)
        end_time = helper.strtime_to_utc(end_time)

        print(start_time, type(start_time))
        pipeline = [{"$match": {"detection_time": {"$gt": start_time, "$lt": end_time}, "staff.notify_enable": 1, "staff.state": 1}},
                    {"$group": {"_id": "$staff.staff_id", "staff_code":{"$first":"$staff.staff_code"}, 
                                "fullname":{"$first":"$staff.fullname"}, "unit": {"$first": "$staff.unit"},
                                "title": {"$first": "$staff.title"},
                                "checkin": {"$min": "$detection_time"}, "checkout": {"$max": "$detection_time"}}},
                    {"$project": {"_id": 0}}]

        result = self.detection_coll.aggregate(pipeline)
        list_data = []
        for res in result:
            list_data.append({'staff_code':res['staff_code'], 'email_code': res.get('email_code'),
                              'fullname':res['fullname'], 'unit':res['unit'], 'title': res['title'],
                            'checkin': helper.datetime_to_str(helper.datetime_from_utc_to_local(res['checkin'])), 
                            'checkout': helper.datetime_to_str(helper.datetime_from_utc_to_local(res['checkout']))})
        return list_data
    
    def sumary_detect_per_person(self, staff_id = None, staff_code = None, staff_name = None, start_time = None, end_time = None):
        start_time = helper.strtime_to_utc(start_time)
        end_time = helper.strtime_to_utc(end_time)

        statement = {}
        statement['timestamp'] = {"$gt": start_time, "$lt": end_time}
        if staff_id != None:
            statement['staff.staff_id'] = staff_id
        if staff_code != None:
            statement['staff.staff_code'] = staff_code
        if staff_name != None:
            statement['staff.fullname'] = {'$regex': staff_name}
        print("statement = ", statement)
        result = self.detection_coll.find(statement, {'_id': 0, 'staff.staff_id': 0})                
        return result
    
mongodb = MongoDatabase()

mariadb_config = {
    'host': settings.MARIADB_HOST,
    'port': settings.MARIADB_PORT,
    'user': settings.MARIADB_USERNAME,
    'password': settings.MARIADB_PASSWORD,
    'database': settings.MARIADB_DB_NAME
}
        
MARIADB_URL = f"mysql+pymysql://root:root@{settings.MARIADB_HOST}:{settings.MARIADB_PORT}/{settings.MARIADB_DB_NAME}"
print("DATABASE_URL = ", MARIADB_URL)
engine = create_engine(MARIADB_URL + '?charset=utf8', echo=True)
BASE = declarative_base(engine)

def get_session():
    with Session(engine) as session:
        yield session
        session.close()

def get_cursor():
    try:
        conn = pymysql.connect(**mariadb_config)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = str(e)
            )
    with conn.cursor() as cursor:
        yield cursor
        cursor.close()
        conn.close()

class DataBase:
    def __init__(self):
        pass

    def get_all(self, session, statement):
        try:
            return session.execute(statement).all()
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = e._message()
            )

    def get_by_id(self, session, statement):
        try:
            orm_ojb = session.execute(statement).all()
            if orm_ojb:
                return orm_ojb[0][0]
            return orm_ojb
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = e._message()
            )

    def add(self, session, orm_obj):
        try:
            session.add(orm_obj)
            session.commit()
            session.refresh(orm_obj)
            return orm_obj
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = e._message()
            )

    def delete(self, session, orm_obj):
        try:
            session.delete(orm_obj)
            session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = e._message()
            )

db = DataBase()