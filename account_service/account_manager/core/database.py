from sqlmodel import SQLModel, create_engine
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import HTTPException, status
import redis
# import mariadb
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import settings
config = {
    'host': settings.MARIADB_HOST,
    'port': settings.MARIADB_PORT,
    'user': settings.MARIADB_USERNAME,
    'password': settings.MARIADB_PASSWORD,
    'database': settings.MARIADB_DB_NAME
}
print("config = ", config)        
DATABASE_URL = f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_HOST}:{settings.MARIADB_PORT}/{settings.MARIADB_DB_NAME}"
print("DATABASE_URL = ", DATABASE_URL)
print("redis_host, redis_port = ", settings.REDIS_HOST, settings.REDIS_PORT)
#mariadb+mariadbconnector://admin:admin@172.21.100.174:3306/xface_test/?charset=utf8
engine = create_engine(DATABASE_URL + '?charset=utf8', echo=True)
BASE = declarative_base(engine)
# print(engine.connect())
# # Create session
# Session = sessionmaker(bind=engine)
# session = Session()
redis_db = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, decode_responses=True)

def conn():
    SQLModel.metadata.create_all(engine, )

def get_session():
    with Session(engine) as session:
        yield session
    # with sessionmaker(engine, expire_on_commit=False, class_=AsyncSession) as session:
    #     yield session

# class Cur:
#     def __init__(self) -> None:
#         self.conn = mariadb.connect(**config)
#         self.cur = self.conn.cursor()

# def get_cur():
#     conn = mariadb.connect(**config)
#     with conn.cursor() as cur:
#         yield cur
#         cur.close()
#         conn.close()
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