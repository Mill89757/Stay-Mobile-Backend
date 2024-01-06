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

# # get redis cache 
r = redis.Redis(host='localhost', port=6379, db=0)



def decoding(item:redis):
    return item.decode('utf-8')

# # -------------------------------------------------------------------------------------




# # --- get table length by the end of previous day ---

# redis_key = db_len
# redis_type = hash table 
# hash_field = table name's abbreviation
# hash_value = table length (in previous day)

clg_len  = r.hget('db_len', 'clg').decode('utf-8')      # challenge 
mmbr_len = r.hget('db_len', 'mmbr').decode('utf-8')     # member
post_len = r.hget('db_len', 'post').decode('utf-8')    
like_len = r.hget('db_len', 'like').decode('utf-8')     
track_len = r.hget('db_len', 'track').decode('utf-8')


# --- use table_len to access record of interest ---

CHALLENGE = session.query(models.Challenge).offset(clg_len)
MEMBER = session.query(models.GroupChallengeMembers).offset(mmbr_len)
POST = session.query(models.Post).offset(post_len)

LIKE = (
    session.query(
        models.UserReactionLog, models.Post.challenge_id
        ).join(
            models.UserReactionLog, models.Post.id == models.UserReactionLog.post_id
        ).order_by(models.UserReactionLog.created_datetime
        ).offset(like_len).all()
    )
# LIKE is a list of tuple, 
# instance[0].__table__.columns.keys() = ['log_id', 'post_id', 'user_id', 'emoji_image', 'created_datetime', 'is_cancelled']
# instance[1] contains info about ['challenge_id']

TRACK = session.query(models.Tracking).offset(track_len)




# --- get recentmost like data (5 days) from the like table ---
# !!!!!!!!!!!!!!!!!!!!!!!!! better to UPDATE RECORD in the end ... !!!!!!!!!!!!!!!!!!!!!!!!

# redis_key = like_record_[1~5]
# redis_type = hash table 
# hash_field = clg_id
# hash_value = user_id separated by comma


ongoing_clg_id = r.hkeys('like_record_1')

for clg in ongoing_clg_id:
    for day in range(1,5):
        day1 = 'like_record_' + str(day)
        day2 = 'like_record_' + str(day+1)
        r.hset(day1, clg, r.hget(day2, clg))
    r.hset('like_record_5', clg, '')




# --- load data about the ongoing challenges ---
# --- this one doesn't really need to be here, this is just a note so that I know how to access data from redis  ---

# redis_key = on_clg_info 
# redis_type = hash
# hash_field = clg_id for which challenges are on going
# hash_value = [category, is_public, finished_date] in string format, separated by comma



# posts_by_categories[i] contains post_id that matches category i 

# redis_key = category_posts 
# redis_type = hash
# hash_field = category code (0, 1, 2, 3, or 4)
# hash_value = post_id belong to this category, separated by comma 





# --- for each user, record number of days they spent on each category ---

# redis_key = user_contribution 
# redis_type = hash
# hash_field = user_id
# hash_value = 5 non-negative integers, separated by comma 



# --- for each user, record new post_id for which challenges that they recently interacted with ---

# redis_key = user_like
# redis_type = hash
# hash_field = user_id
# hash_value = post_id sepearated by comma 





# -------------------------------------------------------------------------------------

# Close the session
session.close()

