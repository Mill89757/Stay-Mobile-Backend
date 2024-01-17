import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
import models
import os
from dotenv import load_dotenv
import datetime 
import pytz


def decoding(item, StrToSplit = None, ifError = None) -> str or list:
    """
    the value retrieved from redis is in binary format.
    this function converts it to string and split it if necessary.
    """
    if item == None:
        return ifError
    item = item.decode('utf-8')
    if StrToSplit: 
        item = item.split(StrToSplit)
        if item == ['']: item = []
    return item


def add_new_ongoing_challenges_to_redis() -> int:
    """
    this function iterate through all newly created challenges. 
    it then stores category, is_public and date info to redis.
    """
    clg_len  = decoding(r.hget('db_len', 'clg'), ifError = 0)      # challenge 
    CHALLENGE = session.query(models.Challenge).offset(clg_len)

    clg_count = 0 

    for instance in CHALLENGE:
        clg_count += 1

        challenge_id = instance.id
        category = instance.category
        isPublic = instance.is_public
        duration = instance.duration
        done_by = (instance.created_time + datetime.timedelta(days = duration)).strftime("%Y-%m-%d")

        r.hset('on_clg_info', challenge_id, f'{category},{isPublic},{duration},{done_by}')

    return clg_count


def update_challenge_distribution_for_users() -> int: 

    mmbr_len = decoding(r.hget('db_len', 'mmbr'), ifError = 0) 
    MEMBER = session.query(models.GroupChallengeMembers).offset(mmbr_len)

    mmbr_count = 0

    for instance in MEMBER:
        mmbr_count += 1

        clg_id = instance.challenge_id
        clg_detail = decoding(r.hget('on_clg_info', clg_id), StrToSplit=',',ifError=[])
        
        if not clg_detail: continue 

        category = int(clg_detail[0])
        duration = int(clg_detail[2])
        
        user_id = instance.user_id


        # get user's current contribution
        contribution = decoding(r.hget('user_contribution',user_id), StrToSplit=',', ifError=['0']*5)

        # modify user contribution according to the challenge's category
        contribution[category] = str( int(contribution[category]) + duration )
        contribution = ','.join(contribution)
        
        # update change to redis 
        r.hset('user_contribution', user_id, contribution)

    return mmbr_count


def classifiy_newPosts_by_challengeCategory() -> tuple:
    """
    every post belongs to 1 challenge, every challenge has its category code.
    this function match post_id to category code (0,1,2,3,4) through challenge_id.
    """

    # remove posts that are older than max_post_age from redis. 
    for i in range(CLG_CATEGORY):
        keyname = 'recent_posts_for_category' + str(i)
        day = (int(DAY_INDEX)+1)%DAYS_BACK
        r.zremrangebyscore(keyname,day,day)


    # retrieve new post records from data base 
    post_len = decoding(r.hget('db_len', 'post'), ifError = 0)
    POST = session.query(models.Post).offset(post_len)

    # if challenge is finished, then we should remove it from the ongoing challenge list. 
    challenge_to_be_removed = []

    # record the number of posts being processed
    post_count = 0 

    for instance in POST:
        post_count += 1

        # get data for challenge_id, post_id, is_breaking_day
        challenge_id = instance.challenge_id
        post_id = instance.id
        is_breaking_day = False
        if instance.written_text == 'I have a break today.':
            is_breaking_day = True

        # get challenge detail 
        clg_detail = decoding(r.hget('on_clg_info', challenge_id), StrToSplit=',')

        if not clg_detail: 
            raise Exception(f"post_id = {post_id}\nThis post does not belong to any challenge")

        category, isPublic, _, doneby = clg_detail
        category = int(category)
        doneby = datetime.datetime.strptime(doneby[:], '%Y-%m-%d')
        
        # add public, non-break post to the list 
        if isPublic and not is_breaking_day:
            r.zadd(f'recent_posts_for_category{category}', {post_id: DAYS_BACK})
            r.hset('post_clg_pair', post_id, challenge_id) # useful in recommend_post_from_interacted_challenges()

        # check whether we should remove this challenge 
        if doneby == DATE_TODAY:
            challenge_to_be_removed.append(challenge_id)

    return post_count, challenge_to_be_removed


def process_recent_reaction_data() -> tuple:
    """
    """

    # read UserReactionLog table
    reaction_len = decoding(r.hget('db_len', 'reaction'), ifError = 0)             # ???????? need to consider daysBack
    REACTION = session.query(models.UserReactionLog).offset(reaction_len)

    reaction_count = 0 

    for instance in REACTION:
        reaction_count += 1

        # if user reacted to a completed clg, then skip it ???????????????????????????????
        post_id = instance.post_id

        clg_id = int(decoding(r.hget('post_clg_pair',post_id), ifError='-1'))
        if clg_id == -1: continue 

        is_cancelled = instance.is_cancelled
        user_id = instance.user_id
        

        # update {user_id}_liked_posts and {user_id}_clgs_preference

        if is_cancelled: 
            r.zincrby(str(user_id)+'_clgs_preference', -0.6, clg_id)
            continue 

        r.sadd(str(user_id)+'_liked_posts', post_id)
        r.zincrby(str(user_id)+'_clgs_preference', 1, clg_id)

    return reaction_count







if __name__ == "__main__":
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





    sydney_tz = pytz.timezone('Australia/Sydney')
    DATE_TODAY = datetime.datetime.now(sydney_tz).date()

    DAYS_BACK = int(decoding(r.hget('rs_param', 'max_post_age'),ifError='7'))
    CLG_CATEGORY = int(decoding(r.hget('rs_param', 'distinct_category'),ifError='5'))

    DAY_INDEX = int(decoding(r.hget('rs_param', 'day_index'),ifError='-1')) + 1
    DAY_INDEX = str(DAY_INDEX%DAYS_BACK)


    new_clg_records = add_new_ongoing_challenges_to_redis()
    update_challenge_distribution_for_users()
    classifiy_newPosts_by_challengeCategory()
    process_recent_reaction_data()
    



    
    # Close the session
    session.close()




