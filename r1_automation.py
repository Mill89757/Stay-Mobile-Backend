import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
import models
import os
from dotenv import load_dotenv
import datetime 
import pytz


CLG_CATEGORY = 5 
MAX_POST_AGE = 80


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


def remove_outdated_clg_and_post_from_redis() -> None:
    outdated_clg = r.zrangebyscore('completed_clg',DAY_INDEX, DAY_INDEX)

    for item in outdated_clg:
        challenge_id = int(decoding(item))

        # get challenge category
        try:
            category = int(decoding(r.hget('on_clg_info', challenge_id), StrToSplit=',')[0])
        except IndexError: 
            raise KeyError(f'challenge {challenge_id} is not found') 

        # remove posts of this challenge from redis 
        for post in r.lrange('clg{challenge_id}posts', 0, -1):
            r.zrem(f'category{category}', post)
            r.hdel('post_clg_pair', post)
        
        # remove challenge detail from redis 
        r.hdel('on_clg_info', challenge_id)
        r.delete(f'clg{challenge_id}posts')
        r.zrem('completed_clg', challenge_id)


def add_new_ongoing_challenges_to_redis() -> None:
    """
    This function iterate through all newly created challenges,
    It extract category, is_public and date information of each new challenge 
    from CHALLENGE table and store into redis.
    Finally, it updates CHALLENGE table's length variable in redis. 
    """
    clg_len  = decoding(r.hget('db_len', 'clg'), ifError = 0)      # challenge 
    CHALLENGE = session.query(models.Challenge).offset(clg_len)

    clg_count = 0 

    for instance in CHALLENGE:
        clg_count += 1

        challenge_id = instance.id
        category = instance.category
        isPublic = 1 if instance.is_public else 0
        duration = instance.duration
        done_by = (instance.created_time + datetime.timedelta(days = duration)).strftime("%Y-%m-%d")

        r.hset('on_clg_info', challenge_id, f'{category},{isPublic},{duration},{done_by}')

    # update table CHALLENGE's length 
    r.hincrby('db_len', 'clg', clg_len)


def update_challenge_distribution_for_users() -> None: 
    """
    Whenever new challenge(s) is/are created, one or more members' contribution 
    to challenge categories is/are changed. 
    This function iterates through the MEMBER table and check on_clg_info (redis) 
    to update members' contributions. 
    Finally, it updates MEMBER table's length variable in redis. 
    """

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

    # update table MEMBER's length
    r.hincrby('db_len', 'mmbr', mmbr_count)  


def classifiy_newPosts() -> None:
    """
    Each post is associated with one challenge, and each challenge has a category code.
    This function examines newly created posts. If a post is public and not mean to be break, 
    its post_id will be recorded in three places in Redis:

    1. As an item in a Redis list named clg{challenge_id}posts.
    2. As a member in a Redis sorted set named category{category_code}.
    3. As a field in a Redis hash table, where the value is its post_id.
    """

    # remove posts that are older than max_post_age from redis. 
    for i in range(CLG_CATEGORY):
        keyname = 'recent_posts_for_category' + str(i)
        day = DAY_INDEX%MAX_POST_AGE
        r.zremrangebyscore(keyname,day,day)

    # retrieve new post records from data base 
    post_len = decoding(r.hget('db_len', 'post'), ifError = 0)
    POST = session.query(models.Post).offset(post_len)

    # record the number of posts being processed
    post_count = 0 

    for instance in POST:
        post_count += 1

        # get data for challenge_id, post_id, is_breaking_day
        challenge_id = instance.challenge_id
        post_id = instance.id
        user_id = instance.user_id

        # check whether this post belong to an ongoing challenge 
        try: # retrieve challenge data 
            category, isPublic, duration, doneby = decoding(r.hget('on_clg_info', challenge_id), StrToSplit=',')
            category, isPublic, duration = int(category), int(isPublic), int(duration)
        except (TypeError, ValueError):
            raise KeyError(f'post_id: {post_id}, challenge_id: {challenge_id}.\nThis challenge is not ongoing.')
        
        # if breaking day, decrement user's contribution
        if instance.written_text == 'I have a break today.':
            contribution = decoding(r.hget('user_contribution',user_id), StrToSplit=',', ifError=['0']*5)
            try: 
                contribution[category] = str(int(contribution[category])-1)
            except IndexError:
                raise IndexError(f'challenge category are from 0 to 4 includive, got {category}')
            else:
                r.hset('user_contribution',user_id,','.join(contribution)) 
                continue

        # if not breaking day and public, add post_id to redis
        if isPublic:
            r.zadd(f'category{category}', {post_id: DAY_INDEX})
            r.hset('post_clg_pair', post_id, challenge_id)
            r.lpush(f'clg{challenge_id}posts', post_id)
        
        # check whether current challenge is completed, record completed challenge 
        # so we can remove related posts from recommended_post_pool soon. 
        if datetime.datetime.strptime(doneby[:], '%Y-%m-%d').date() <= DATE_TODAY:
            if duration <= 14: 
                due_day_index = (DAY_INDEX + 20) % MAX_POST_AGE
            elif duration <= 35:
                due_day_index = (DAY_INDEX + 40) % MAX_POST_AGE
            elif duration <= 49:
                due_day_index = (DAY_INDEX + 60) % MAX_POST_AGE
            else:
                due_day_index = (DAY_INDEX + 80) % MAX_POST_AGE
            r.zadd('completed_clg', {challenge_id: due_day_index})

    # update table POST's length 
    r.hincrby('db_len', 'post', post_count)  


def process_recent_reaction_data() -> None:
    """
    this function add post_id and  challenge_id of newly generated reaction data to 
    the corresponding Redis set with user_id as main part of the key.
    """

    # read UserReactionLog table
    reaction_len = decoding(r.hget('db_len', 'reaction'), ifError = 0)
    REACTION = session.query(models.UserReactionLog).offset(reaction_len)

    reaction_count = 0 

    for instance in REACTION:
        reaction_count += 1

        # get post_id, challenge_id, user_id, reaction_status (is_cancelled)
        post_id = instance.post_id
        try: 
            challenge_id = int(decoding(r.hget('post_clg_pair',post_id)))
        except TypeError:
            continue 
        user_id = instance.user_id
        is_cancelled = instance.is_cancelled

        # recalling a reaction is something negative, so decrement challenge preference
        if is_cancelled: 
            r.zincrby(str(user_id)+'_clgs_preference', -0.6, challenge_id)
        else: 
            r.sadd(str(user_id)+'_reacted_post_pool', post_id)
            r.zincrby(str(user_id)+'_clgs_preference', 1, challenge_id)

    r.hincrby('db_len', 'reaction', reaction_count)  


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

    DAY_INDEX = (int(decoding(r.get('day_index'),ifError='-1')) + 1) % MAX_POST_AGE
    r.set('day_index', DAY_INDEX)


    remove_outdated_clg_and_post_from_redis()
    add_new_ongoing_challenges_to_redis()
    update_challenge_distribution_for_users()
    classifiy_newPosts()
    process_recent_reaction_data()

    
    # Close the session
    session.close()




