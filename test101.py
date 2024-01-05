import redis
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import models
import os

from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}@{os.environ['DATABASE_HOST']}/{os.environ['DATABASE_NAME']}"

# Define your database connection here (SQLite for example)
engine = create_engine(SQLALCHEMY_DATABASE_URL)  

# Base class for your model classes
Base = declarative_base()

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Query the database for records where the name matches `name_to_search`
for instance in session.query(models.User).order_by(models.User.id):
    print(instance.id)
    


# Close the session
session.close()


if __name__ == "__main__":
    pass