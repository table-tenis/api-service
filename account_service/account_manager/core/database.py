from sqlmodel import SQLModel, create_engine
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import HTTPException, status
import redis
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import settings
      
DATABASE_URL = f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_HOST}:{settings.MARIADB_PORT}/{settings.MARIADB_DB_NAME}"
print("DATABASE_URL = ", DATABASE_URL)
print("redis_host, redis_port = ", settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD)
engine = create_engine(DATABASE_URL + '?charset=utf8', echo=True)
BASE = declarative_base(engine)
redis_db = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, decode_responses=True)

def conn():
    SQLModel.metadata.create_all(engine, )

def get_session():
    with Session(engine) as session:
        yield session
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