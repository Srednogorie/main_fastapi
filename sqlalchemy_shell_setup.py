import sys

from app.models.foo import *
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, joinedload

engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/fastapi", echo=True)

session = sessionmaker(bind=engine, future=True)
session = session()

sys.path.append("/Users/apple/Development/projects/main_api")

