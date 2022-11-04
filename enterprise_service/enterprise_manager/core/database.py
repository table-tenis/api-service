from sqlmodel import SQLModel, create_engine
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import APIRouter, HTTPException, status
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import settings
        
MARIADB_URL = f"mysql+pymysql://root:root@{settings.MARIADB_HOST}:{settings.MARIADB_PORT}/{settings.MARIADB_DB_NAME}"
print("DATABASE_URL = ", MARIADB_URL)
engine = create_engine(MARIADB_URL + '?charset=utf8', echo=True)
BASE = declarative_base(engine)

def get_session():
    with Session(engine) as session:
        yield session
        session.close()

def get_cursor():
    with engine.raw_connection().cursor() as cursor:
        yield cursor
        cursor.close()

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