# import redis
# from sqlalchemy import create_engine, Column, String, Integer
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import models
# import os

# from dotenv import load_dotenv

# load_dotenv()

# SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}@{os.environ['DATABASE_HOST']}/{os.environ['DATABASE_NAME']}"

# # Define your database connection here (SQLite for example)
# engine = create_engine(SQLALCHEMY_DATABASE_URL)  

# # Base class for your model classes
# Base = declarative_base()

# # Create a session to interact with the database
# Session = sessionmaker(bind=engine)
# session = Session()




# clg_len = 20
# CHALLENGE = session.query(models.Challenge).offset(clg_len)
# for instance in CHALLENGE:
#     print(instance.id)






# # # Query the database for records where the name matches `name_to_search`
# # for instance in session.query(models.Challenge):
# #     print(instance.id, end=', ')

# # print()

# # for instance in session.query(models.Challenge).offset(10):
# #     print(instance.id, end=', ')


# # Close the session
# session.close()


# if __name__ == "__main__":
#     pass




import redis
from sqlalchemy import create_engine
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





clg_len = 30
CHALLENGE = session.query(models.Challenge).offset(clg_len)
for instance in CHALLENGE:
    print(instance.created_time)
    break


# LIKE = session.query(models.UserReactionLog)
# for instance in LIKE:
#     print(instance.id)



# Close the session
session.close()