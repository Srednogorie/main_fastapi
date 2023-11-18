import sys

from app import settings
from app.models.foo import *
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, joinedload

engine = create_engine(f"postgresql://postgres:postgres@host.docker.internal:5432/{settings.app_name}", echo=True)

session = sessionmaker(bind=engine, future=True)
session = session()

sys.path.append("/Users/apple/Development/projects/main_api")
