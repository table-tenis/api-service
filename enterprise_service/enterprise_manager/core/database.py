from sqlmodel import SQLModel, create_engine
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import redis
import mariadb
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import settings
config = {
    'host': '127.0.0.1',
    'port': 3308,
    'user': 'root',
    'password': 'root',
    'database': 'xface_system'
}
        
DATABASE_URL = f"mariadb+mariadbconnector://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.database_name}"
print("DATABASE_URL = ", DATABASE_URL)
engine = create_engine('mariadb+mariadbconnector://root:root@172.21.100.174:3306/xface_system', echo=True)
BASE = declarative_base(engine)
# print(engine.connect())
# # Create session
# Session = sessionmaker(bind=engine)
# session = Session()

redis_db = redis.Redis(host='localhost', port=6379, decode_responses=True)

def conn():
    SQLModel.metadata.create_all(engine, )

def get_session():
    with Session(engine) as session:
        yield session
    # with sessionmaker(engine, expire_on_commit=False, class_=AsyncSession) as session:
    #     yield session

class Cur:
    def __init__(self) -> None:
        self.conn = mariadb.connect(**config)
        self.cur = self.conn.cursor()

def get_cur():
    conn = mariadb.connect(**config)
    with conn.cursor() as cur:
        yield cur
        cur.close()
        conn.close()