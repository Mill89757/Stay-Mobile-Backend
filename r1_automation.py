import redis
from sqlalchemy import create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
import models
import os
from dotenv import load_dotenv
import datetime 
import pytz


CLG_CATEGORY = 5 
MAX_POST_AGE = 30
r = redis.Redis(host='localhost', port=6379, db=0)

def byte_to_utf8(item: bytes or str, multiple_items = False, StrToSplit:str = None):
    """
    param item: a bytes or string object.
    param multiple_items: True if item is a sequence of bytes objects, False otherwise. 
    param StrToSplit: character(s) to separate a sequence of objects.

    This function first turn the given item into utf-8 string, 
    or a sequence of string objects if StrToSplit is given.

    It then converts the string into an object of preferrable type. 
    """

    if item == None:
        return None
    
    if isinstance(item, bytes):
        item = item.decode('utf-8')
    
    # base case: not a list or sequence of items. 
    if not StrToSplit and not multiple_items:

        try:
            # item is numeric 
            item = float(item)
        except ValueError: # item is indeed a string
            pass  
        else:
            if int(item) == item:
                item = int(item)
        finally:
            return item 

    # general case: item is a sequence of object 
    if not multiple_items:
        item = item.split(StrToSplit)

    for i in range(len(item)):
        item[i] = byte_to_utf8(item[i])

    return [] if item == [''] else item  


def getRedisValue(key:str or bytes, hash_field = None, ranges = None, score=None, splitOn = None, onError=None, r:redis=r): 
    """
    param key: a redis key
    param hash_field: this refers to the filed name in redis hash table
    param ranges: if specified, return sequence[ranges[0]...ranges[1]].
    param score: this refers to the score values in sorted set.
    param splitOn: a string used as spliting character in redis string object.
    param onError: the returned value if the key doesn't exist. 

    this function use 'key' and other parameters to access value scored in the Redis database. 
    retrun: the value of Redis key in utf8 format. 
    """

    value = None
    if r.type(key) == b'string':
        value = r.get(key)
        value = byte_to_utf8(value)
    elif r.type(key) == b'hash':
        value = r.hget(key, hash_field)
        value = byte_to_utf8(value, StrToSplit=splitOn)
    elif r.type(key) == b'list':
        if ranges:
            value = r.lrange(key, ranges[0], ranges[1])
        else: 
            value = r.lrange(key,0,-1)
        value = byte_to_utf8(value, multiple_items=True)
    elif r.type(key) == b'set':
        value = r.smembers(key)
        value = list(value)
        value = byte_to_utf8(value, multiple_items=True)
        value = set(value)
    elif r.type(key) == b'zset':
        if score:
            value = r.zrangebyscore(key,score[0],score[1])
        elif ranges:
            value = r.zrange(key, ranges[0],ranges[1])
        else:
            value = r.zrange(key, 0, -1)
        value = byte_to_utf8(value, multiple_items=True)    

    if value: return value
    else: return onError



def setRedisValue(key:str or list, key_type:str, value: str or list, method:str = 'set') -> None:
    """
    key: redis key, (key pair for hash table object).
    key_type: one of 'str', 'hash', 'list', 'set', 'zset'
    value: the value to be stored into redis. ([value,store] for zset). 
    method: one of 'set', 'incr', 'update', 'push left', 'push right' 

    this function store key value pair into redis, it can also modify values. 
    """
    if key_type == 'str':
        if method == 'incr': r.incrby(key,value)
        elif method == 'set': r.set(key, value)
    elif key_type == 'hash':
        if method == 'set': 
            r.hset(key[0], key[1], value)
        elif method == 'incr':
            r.hincrby(key[0],key[1], value)
    elif key_type == 'list':
        if method == 'push left':
            r.lpush(key,value)
        elif method == 'push right' or method =='set':
            r.rpush(key,value)
    elif key_type == 'set':
        if method == 'set':
            r.sadd(key, value)
    elif key_type == 'zset':
        if method == 'set' or method == 'update':
            r.zadd(key, {value[0]:value[1]})
        elif method == 'incr':
            r.zincrby(key, value[1], value[0])
        



def remove_outdated_clg_and_post_from_redis() -> None:
    outdated_clg = getRedisValue('completed_clg',score=[DAY_INDEX,DAY_INDEX],onError=[])

    for challenge_id in outdated_clg:

        # get challenge category
        try:
            category = getRedisValue('on_clg_info',challenge_id,splitOn=',')[0]
        except IndexError: 
            raise KeyError(f'challenge {challenge_id} is not found') 

        # remove posts of this challenge from redis 
        for post in getRedisValue(f'clg{challenge_id}posts'):
            r.zrem(f'category{category}post', post)
            r.hdel('post_clg_pair', post)
        
        # remove challenge detail from redis 
        r.hdel('on_clg_info', challenge_id)
        r.delete(f'clg{challenge_id}posts')
        r.zrem('completed_clg', challenge_id)


def add_new_ongoing_challenges_to_redis() -> None:
    """
    For every new challenges, this function add {challenge_id: 'category,is_public,
    duration,done_by' as field value pair to redis object called on_clg_info/

    Record the updated table length in the end. 
    """
    clg_len = getRedisValue('db_len', 'clg', onError=0) 
    CHALLENGE = session.query(models.Challenge).offset(clg_len)

    clg_count = 0 

    for instance in CHALLENGE:
        clg_count += 1

        challenge_id = instance.id
        category = instance.category
        isPublic = 1 if instance.is_public else 0
        duration = instance.duration
        done_by = (instance.created_time + datetime.timedelta(days = duration)).strftime("%Y-%m-%d")

        value = f'{category},{isPublic},{duration},{done_by}'
        setRedisValue(['on_clg_info', challenge_id], 'hash', value)

    # update table CHALLENGE's length 
    setRedisValue(['db_len', 'clg'], 'hash', clg_count, 'incr')


def update_challenge_distribution_for_users() -> None: 
    """
    This function iterate through new records in GroupChallengeMembers. 
    For users with new challenges, update his/her contribution on challenge 
    categories based on the duration of the new challenge. 
    
    Record the updated table length in the end. 
    """

    mmbr_len = getRedisValue('db_len', 'mmbr',onError=0)
    MEMBER = session.query(models.GroupChallengeMembers).offset(mmbr_len)

    mmbr_count = 0

    for instance in MEMBER:
        mmbr_count += 1

        challenge_id = instance.challenge_id
        clg_detail = getRedisValue('on_clg_info', challenge_id, splitOn=',', onError=[])
        
        if not clg_detail: continue 

        category = clg_detail[0]
        duration = clg_detail[2]
        
        user_id = instance.user_id


        # get user's current contribution
        contribution = getRedisValue('user_contribution', user_id, splitOn=',',onError=[0]*5)

        # modify user contribution according to the challenge's category
        contribution[category] += duration
        contribution = [str(num) for num in contribution]
        contribution = ','.join(contribution)
        
        # update change to redis 
        setRedisValue(['user_contribution', user_id], 'hash', contribution)

    # update table MEMBER's length
    setRedisValue(['db_len', 'mmbr'], mmbr_count, 'incr')


def classify_newPosts() -> None:
    """
    Each post is associated with one challenge, and each challenge has a category code.
    This function examines newly created posts. If a post is public and not mean to be break, 
    its post_id will be recorded in three places in Redis:

    1. add to a list named clg{challenge_id}posts
    2. add to a sorted set named category{category_code}post.
    3. add to hash table named post_clg_pair, where the value is its post_id.
    """

    # remove posts that are older than max_post_age from redis. 
    for i in range(CLG_CATEGORY):
        keyname = f'category{i}post'
        r.zremrangebyscore(keyname,DAY_INDEX,DAY_INDEX)

    # retrieve new post records from data base 
    post_len = getRedisValue('db_len', 'post', onError=0)
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
            category, isPublic, duration, doneby = getRedisValue('on_clg_info', challenge_id, splitOn=',')
        except (TypeError, ValueError):
            raise KeyError(f'post_id: {post_id}, challenge_id: {challenge_id}.\nThis challenge is not ongoing.')
        
        # if breaking day, decrement user's contribution
        if instance.written_text == 'I have a break today.':
            contribution = getRedisValue('user_contribution',user_id, splitOn=',', onError=[0]*5)
            try: 
                contribution[category]-=1
            except IndexError:
                raise IndexError(f'challenge category are from 0 to 4 includive, got {category}')
            else:
                contribution = [str(num) for num in contribution]
                contribution = ','.join(contribution)
                setRedisValue(['user_contribution',user_id],'hash', contribution)
                continue
        
        ##### testing #####
        if not os.path.exists('redis_output'):
            os.makedirs('redis_output')
        if not r.exists(f'clg{challenge_id}posts'):
            with open('./redis_output/clg_posts.txt', 'a') as f:
                f.write(f'clg{challenge_id}posts')
                f.write(',')
        ##### testing #####

        # if not breaking day and public, add post_id to redis
        if isPublic:
            setRedisValue(f'category{category}post', 'zset', [post_id, DAY_INDEX])
            setRedisValue(['post_clg_pair', post_id], 'hash', challenge_id)
            setRedisValue(f'clg{challenge_id}posts','list', post_id, 'push left')
        
        # check whether current challenge is completed, record completed challenge 
        # so we can remove related posts from recommended_post_pool soon. 
        if datetime.datetime.strptime(doneby[:], '%Y-%m-%d').date() == DATE_TODAY:
            if duration <= 14: 
                due_day_index = (DAY_INDEX + MAX_POST_AGE//5) % MAX_POST_AGE
            elif duration <= 35:
                due_day_index = (DAY_INDEX + MAX_POST_AGE//4) % MAX_POST_AGE
            elif duration <= 49:
                due_day_index = (DAY_INDEX + MAX_POST_AGE//3) % MAX_POST_AGE
            else:
                due_day_index = (DAY_INDEX + MAX_POST_AGE//2) % MAX_POST_AGE
            setRedisValue('completed_clg', 'zset', [challenge_id, due_day_index])

    # update table POST's length 
    setRedisValue(['db_len', 'post'], 'hash', post_count, 'incr')


def process_recent_reaction_data() -> None:
    """
    this function add post_id and challenge_id of newly generated reaction data to 
    the corresponding Redis set with user_id as main part of the key.
    """

    # read UserReactionLog table
    reaction_len = getRedisValue('db_len', 'reaction', onError=0)
    REACTION = session.query(models.UserReactionLog).offset(reaction_len)

    reaction_count = 0 

    for instance in REACTION:
        reaction_count += 1

        # get post_id, challenge_id, user_id, reaction_status (is_cancelled)
        post_id = instance.post_id
        challenge_id = getRedisValue('post_clg_pair',post_id)
        if challenge_id == None: continue 
        user_id = instance.user_id
        is_cancelled = instance.is_cancelled


        ##### testing ##### 
        if not os.path.exists('redis_output'):
            os.makedirs('redis_output')
        if not r.exists(f'{user_id}_clgs_preference'):
            with open('./redis_output/user_clgs_preference.txt', 'a') as f:
                f.write(f'{user_id}_clgs_preference')
                f.write(',')
        if not r.exists(f'{user_id}_reacted_post_pool'):
            with open('./redis_output/user_reacted_post_pool.txt', 'a') as f:
                f.write(f'{user_id}_reacted_post_pool')
                f.write(',')
        ##### testing #####
            
        # recalling a reaction is something negative, so decrement challenge preference
        if is_cancelled: 
            setRedisValue(f'{user_id}_clgs_preference','zset',[challenge_id, -0.6], 'incr')
        else: 
            setRedisValue(f'{user_id}_reacted_post_pool','set', post_id)
            setRedisValue(f'{user_id}_clgs_preference', 'zset', [challenge_id, 1], 'incr')

    setRedisValue(['db_len', 'reaction'], 'hash', reaction_count, 'incr')







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

    DAY_INDEX = (getRedisValue('day_index', onError=-1) + 1) % MAX_POST_AGE
    setRedisValue('day_index', 'str', DAY_INDEX)






    try:
        remove_outdated_clg_and_post_from_redis()
        add_new_ongoing_challenges_to_redis()
        update_challenge_distribution_for_users()
        classify_newPosts()
        process_recent_reaction_data()

    except Exception as e:

        keys = ['db_len', 'day_index', 'on_clg_info', 'user_contribution', 'post_clg_pair', 'completed_clg']
        for key in keys: r.delete(key)
        for i in range(5): r.delete(f'category{i}post')

        folder = "./redis_output"
        file_list = os.listdir(folder)
        for filename in file_list:
            file = f'{folder}/{filename}'
            with open(file, 'r') as f:
                keys = f.readline().split(',')
                for key in keys: 
                    if key: r.delete(key)
            if os.path.exists(file):
                os.remove(file)
        raise(e)
    
    else: 
        print('Automation process is completed!')



    # Close the session
    session.close()