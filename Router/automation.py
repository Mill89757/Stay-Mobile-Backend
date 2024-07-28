import datetime

import pytz
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import models
from database import get_db
from redis_client import redis_client

router = APIRouter()


def decoding(item, str_split_symbol=None, error_result=None) -> str or list:  # type: ignore
    """
    the value retrieved from redis is in binary format.
    this function converts it to string and split it if necessary.
    """
    if not item:
        return error_result
    item = item.decode('utf-8')
    if str_split_symbol:
        item = item.split(str_split_symbol)
        if item == ['']:
            item = []
    return item


def add_new_ongoing_challenges_to_redis(db: Session) -> int:
    """
    this function iterate through all newly created challenges. 
    it then stores category, is_public and date info to redis.
    """
    clg_len = decoding(redis_client.hget('db_len', 'clg'),
                       error_result=0)
    challenge = db.query(models.Challenge).offset(clg_len)

    clg_count = 0

    for instance in challenge:
        clg_count += 1

        challenge_id = instance.id
        category = instance.category
        is_public = instance.is_public
        duration = instance.duration
        done_by = (instance.created_time +
                   datetime.timedelta(days=duration)).strftime("%Y-%m-%d")

        redis_client.hset('on_clg_info', challenge_id,
                          f'{category},{is_public},{duration},{done_by}')

    return clg_count


def update_challenge_distribution_for_users(db: Session) -> int:
    """ Update user contribution based on the challenge category """

    mmbr_len = decoding(redis_client.hget('db_len', 'mmbr'), error_result=0)
    member = db.query(models.GroupChallengeMembers).offset(mmbr_len)

    mmbr_count = 0

    for instance in member:
        mmbr_count += 1

        clg_id = instance.challenge_id
        clg_detail = decoding(redis_client.hget(
            'on_clg_info', clg_id), str_split_symbol=',', error_result=[])

        if not clg_detail:
            continue

        category = int(clg_detail[0])
        duration = int(clg_detail[2])

        user_id = instance.user_id

        # get user's current contribution
        contribution = decoding(redis_client.hget(
            'user_contribution', user_id), str_split_symbol=',', error_result=['0']*5)

        # modify user contribution according to the challenge's category
        contribution[category] = str(int(contribution[category]) + duration)
        contribution = ','.join(contribution)

        # update change to redis
        redis_client.hset('user_contribution', user_id, contribution)

    return mmbr_count


def classify_new_posts_by_challenge_category(db: Session) -> tuple:
    """
    every post belongs to 1 challenge, every challenge has its category code.
    this function match post_id to category code (0,1,2,3,4) through challenge_id.
    """

    # remove posts that are older than max_post_age from redis.
    for i in range(CLG_CATEGORY):
        key_name = 'recent_posts_for_category' + str(i)
        day = (int(DAY_INDEX)+1) % DAYS_BACK
        redis_client.zremrangebyscore(key_name, day, day)

    # retrieve new post records from data base
    post_len = decoding(redis_client.hget('db_len', 'post'), error_result=0)
    post = db.query(models.Post).offset(post_len)

    # if challenge is finished, then we should remove it from the ongoing challenge list.
    challenge_to_be_removed = []

    # record the number of posts being processed
    post_count = 0

    for instance in post:
        post_count += 1

        # get data for challenge_id, post_id, is_breaking_day
        challenge_id = instance.challenge_id
        post_id = instance.id
        is_breaking_day = False
        if instance.written_text == 'I have a break today.':
            is_breaking_day = True

        # get challenge detail
        clg_detail = decoding(redis_client.hget(
            'on_clg_info', challenge_id), str_split_symbol=',')

        if not clg_detail:
            raise ValueError("post not belong to any challenge")
        category, is_public, _, finished_date = clg_detail
        category = int(category)
        finished_date = datetime.datetime.strptime(
            finished_date[:], '%Y-%m-%d')

        # add public, non-break post to the list
        if is_public and not is_breaking_day:
            redis_client.zadd(f'recent_posts_for_category{category}', {
                              post_id: DAYS_BACK})
            # useful in recommend_post_from_interacted_challenges()
            redis_client.hset('post_clg_pair', post_id, challenge_id)

        # check whether we should remove this challenge
        if finished_date == DATE_TODAY:
            challenge_to_be_removed.append(challenge_id)
    return post_count, challenge_to_be_removed


def process_recent_reaction_data(db: Session) -> tuple:
    """ Process recent reaction data and update user's liked posts and clgs preference """
    reaction_len = decoding(redis_client.hget(
        'db_len', 'reaction'), error_result=0)
    reaction = db.query(models.UserReactionLog).offset(reaction_len)

    reaction_count = 0

    for instance in reaction:
        reaction_count += 1

        # if user reacted to a completed clg, then skip it
        post_id = instance.post_id

        clg_id = int(decoding(redis_client.hget(
            'post_clg_pair', post_id), error_result='-1'))
        if clg_id == -1:
            continue

        is_cancelled = instance.is_cancelled
        user_id = instance.user_id

        # update {user_id}_liked_posts and {user_id}_clgs_preference
        if is_cancelled:
            redis_client.zincrby(str(user_id)+'_clgs_preference', -0.6, clg_id)
            continue

        redis_client.sadd(str(user_id)+'_liked_posts', post_id)
        redis_client.zincrby(str(user_id)+'_clgs_preference', 1, clg_id)

    return reaction_count


# update recommendation
sydney_tz = pytz.timezone('Australia/Sydney')
DATE_TODAY = datetime.datetime.now(sydney_tz).date()
DAYS_BACK = int(decoding(redis_client.hget('rs_param', 'max_post_age'), error_result='7'))
CLG_CATEGORY = int(decoding(redis_client.hget('rs_param', 'distinct_category'), error_result='5'))
DAY_INDEX = int(decoding(redis_client.hget('rs_param', 'day_index'), error_result='-1')) + 1
DAY_INDEX = str(DAY_INDEX % DAYS_BACK)

@router.get("/UpdateRecommendation/", status_code=status.HTTP_200_OK)
async def update_recommendation(db: Session = Depends(get_db)):
    """ Update recommendation data in redis """
    update_challenge_distribution_for_users(db=db)
    classify_new_posts_by_challenge_category(db=db)
    process_recent_reaction_data(db=db)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Recommendation updated successfully"})
