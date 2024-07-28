import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# loads environment variables from .env file
load_dotenv()

DATABASE_USER = os.environ['DATABASE_USER']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_NAME = os.environ['DATABASE_NAME']

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
)

# create a SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a Base class to create database classes
Base = declarative_base()


def get_db():
    """ Get a database session """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
