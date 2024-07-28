import os
import random

from dotenv import load_dotenv
from sqlalchemy import create_engine, desc, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import models
from r1_automation import CLG_CATEGORY, get_redis_value
from redis_client import r

# Load environment variables
load_dotenv()

# Connect to the database
DATABASE_USER = os.environ['DATABASE_USER']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_NAME = os.environ['DATABASE_NAME']

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
)

# Set up SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def top3_categories(user_id: int) -> list:
    """
    the 'user_contribution' key in redis is a hash table 
    that record user's contribution to each challenge category.

    this function takes user_id as input and return 3 
    categories where the user has spent the most time contributing.
    """

    # retrive user's challenge contribution data.

    contribution = get_redis_value(
        'user_contribution', user_id, split_symbol=',')
    if not contribution:
        return []
    contribution = {idx: item for idx, item in enumerate(contribution)}

    # randomly shuffle category code
    categories = list(range(CLG_CATEGORY))
    random.shuffle(categories)

    top_categories = []

    for category in categories:

        # if user did not contribute to category i, then move on to the next category
        if contribution[category] == 0:
            continue

        # otherwise, see if user's contribution is one of the top 3 cateogries.
        for i, top_category in enumerate(top_categories):
            if contribution[category] > contribution[top_category]:
                top_categories.insert(i, category)
                continue
        if len(top_categories) < 3:
            top_categories.append(category)
        elif len(top_categories) > 3:
            top_categories.pop()

    # if user contributed to less than 3 categories,
    # then randomly pick some other categories for this user
    n = len(top_categories)
    if n == 3:
        return top_categories
    other_categories = [item for item in [
        0, 1, 2, 3, 4] if item not in top_categories]
    return top_categories + random.sample(other_categories, 3-n)


def remove_outdated_clg_from_user_records(user_id: int, reacted_clgs: list) -> list:
    """ Remove outdated challenges from user's record """
    ongoing_clg = []

    for challenge_id in reacted_clgs:

        if not get_redis_value('on_clg_info', challenge_id, error_result=None):
            r.zrem(f'{user_id}_clg_preference', challenge_id)
        else:
            ongoing_clg.append(challenge_id)

    return ongoing_clg


def get_reacted_challenges(user_id: int) -> set:
    """
    This function takes user_id as input, it then return unreacted posts from selected challenges 
    that the user has recently engaged with. (maximum 200 posts from 20 challenges)
    """

    # get a list of user reacted challenges
    ongoing_clg = remove_outdated_clg_from_user_records(
        user_id=user_id,
        reacted_clgs=get_redis_value(
            f'{user_id}_clgs_preference', error_result=[])[::-1]
    )

    # randomly select a few challenges from reacted_clgs
    candidate_clgs = []

    for challenge_id in ongoing_clg:

        # randomly pick recent challenges as candidate challenge
        if len(candidate_clgs) < 10:
            candidate_clgs.append(challenge_id)
        else:
            if random.randint(0, 10) <= 4:
                candidate_clgs.append(challenge_id)

    if len(candidate_clgs) > 20:
        candidate_clgs = candidate_clgs[:10] + \
            random.sample(candidate_clgs[10:], 10)

    return candidate_clgs


def get_unreacted_posts_from_reacted_challenges(user_id: int) -> set:
    """ Get unreacted posts from user reacted challenges """

    candidate_clgs = get_reacted_challenges(user_id)

    post_pool = set()

    for challenge_id in candidate_clgs:

        n = r.llen(f'clg{challenge_id}posts')
        if n == 0:
            continue

        post_pool = post_pool.union(filter_posts(
            new_posts=random.sample(
                r.lrange(f'clg{challenge_id}posts', 0, -1), min(int(n/10)+1, 10)),
            existing_posts=get_redis_value(f'{user_id}_reacted_post_pool', error_result=set()))
        )

    return post_pool


def get_unreacted_posts_from_top3_categories(user_id: int, top3) -> set:
    """ Get unreacted posts from top 3 categories """
    post_pool = set()

    for category_code in top3:

        # get all recent post from specified category
        raw_post_pool = r.zrangebyscore(
            f'category{category_code}post', 0, float('inf'))
        raw_post_pool = [int(post) for post in raw_post_pool]
        n = len(raw_post_pool)
        if n == 0:
            continue

        post_pool = post_pool.union(filter_posts(
            new_posts=random.sample(raw_post_pool, min(int(n*0.2 + 1), 50)),
            existing_posts=get_redis_value(f'{user_id}_reacted_post_pool', error_result=set()))
        )

    return post_pool


def get_popular_posts() -> list:
    """
    this function get recent popular posts from PostReaction database. 
    """
    # step 1: skip rows
    k = get_redis_value('postReaction', ranges=[0, 0], error_result=0)
    recent_posts = session.query(models.PostReaction).offset(k).subquery()

    # step 2: group by post_id, sum the count column, order by popularity
    post_by_popularity = session.query(
        recent_posts.c.post_id,
        func.sum(recent_posts.c.count).label(  # pylint: disable=not-callable
            'total_count')
    ).group_by(recent_posts.c.post_id
               ).order_by(desc('total_count'))

    # step 3: limit to the first 500 records (or less if there are fewer rows)
    #         then filter for unreacted posts
    return [instance.post_id for instance in post_by_popularity.limit(500).all()]


def get_unreacted_popular_posts(user_id: int, n: int):
    """ Get unreacted popular posts """
    post_pool = set()
    popular_posts = get_popular_posts()
    post_pool = post_pool.union(filter_posts(
        new_posts=popular_posts,
        existing_posts=get_redis_value(f'{user_id}_reacted_post_pool', error_result=set()))
    )
    return set(random.sample(list(post_pool), min(n, len(post_pool))))


def filter_posts(new_posts, existing_posts):
    """ Filter out posts that user has already reacted to """

    if not isinstance(new_posts, set):
        new_posts = set(new_posts)
    if not existing_posts:
        return new_posts

    if not isinstance(existing_posts, set):
        existing_posts = set(existing_posts)
    return new_posts.difference(existing_posts)


def get_recommended_post(user_id):
    """ Get recommended posts """
    post_pool = set()

    # get posts from top 3 categories
    top3_posts = top3_categories(user_id)
    if len(top3_posts) == 0:
        post_pool = post_pool.union(
            get_unreacted_posts_from_top3_categories(user_id, top3_posts))

    # get new posts from user reacted challenges
    post_pool = post_pool.union(
        get_unreacted_posts_from_reacted_challenges(user_id))

    # get recent posts that are popular in general
    post_pool = post_pool.union(get_unreacted_popular_posts(
        user_id, min(30, 100-len(post_pool))))

    return post_pool


if __name__ == "__main__":

    ##### test start #####

    def group_testing(user_group, group_desc):
        """ Test the recommendation system on a group of users """
        print('\n')
        print(f'# ------ {group_desc} ------')

        for user_id in user_group:
            print('\n')

            print(f'user_id: {user_id}')
            top3 = top3_categories(user_id)
            print(f'top3: {top3}')

            post_from_category = get_unreacted_posts_from_top3_categories(
                user_id, top3)
            print(f'post from category:{post_from_category}')

            post_from_reaction = get_unreacted_posts_from_reacted_challenges(
                user_id)
            print(f'post from reaction:{post_from_reaction}')

            post_by_popularity = get_unreacted_popular_posts(user_id, n=5)
            print(f'the popular posts: {post_by_popularity}')

            print(f'recommended posts --> {get_recommended_post(user_id)}')

    groups = [
        ([-1, -2, -3], 'cold start'),
        ([10000, 10001, 10002], 'user with some challenge'),
        ([1, 2, 3, 4, 5], 'users with reaction data')
    ]

    for members, group_description in groups:
        group_testing(members, group_description)

    ##### test finished #####

    session.close()
