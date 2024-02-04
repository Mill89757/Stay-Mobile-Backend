import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import models
import random 
from r1_automation import getRedisValue, byte_to_utf8, CLG_CATEGORY
import redis


r = redis.Redis(host='localhost', port=6379, db=0)

def top3categories(user_id:int) -> list:
    """
    the 'user_contribution' key in redis is a hash table that record user's contribution to each challenge category.
    this function takes user_id as input and return 3 categories where the user has spent the most time contributing.
    """
    
    # retrive user's challenge contribution data.

    contribution = getRedisValue('user_contribution',user_id, splitOn=',')
    if not contribution: return []
    contribution = {idx:item for idx,item in enumerate(contribution)}

    # randomly shuffle category code
    categories = list(range(CLG_CATEGORY))
    random.shuffle(categories)

    topCategories = []

    for category in categories:
        
        # if user did not contribute to category i, then move on to the next category
        if contribution[category] == 0: continue 

        # otherwise, see if user's contribution is one of the top 3 cateogries. 
        for i in range(len(topCategories)):
            if contribution[category] > contribution[topCategories[i]]: 
                topCategories.insert(i, category)
                continue
        if len(topCategories) < 3: 
            topCategories.append(category)
        elif len(topCategories) > 3:
            topCategories.pop()

    # if user contributed to less than 3 categories, 
    # then randomly pick some other categories for this user
    n = len(topCategories)
    if n == 3:
        return topCategories
    other_categories = [item for item in [0,1,2,3,4] if item not in topCategories]
    return  topCategories + random.sample(other_categories, 3-n)


def remove_outdated_clg_from_user_records(user_id:int, reacted_clgs:list) -> list:

    ongoing_clg = []

    for challenge_id in reacted_clgs:

        if not getRedisValue('on_clg_info', challenge_id, onError=None, r=r):
            r.zrem(f'{user_id}_clg_preference',challenge_id)
        else: ongoing_clg.append(challenge_id)

    return ongoing_clg


def get_reacted_challenges(user_id:int) -> set:
    """
    This function takes user_id as input, it then return unreacted posts from selected challenges 
    that the user has recently engaged with. (maximum 200 posts from 20 challenges)
    """

    # get a list of user reacted challenges
    ongoing_clg = remove_outdated_clg_from_user_records(
                    user_id=user_id,
                    reacted_clgs=getRedisValue(f'{user_id}_clgs_preference', onError=[], r=r)[::-1]
                    )

    # randomly select a few challenges from reacted_clgs
    candidate_clgs = []

    for challenge_id in ongoing_clg:

        # randomly pick recent challenges as candidate challenge
        if len(candidate_clgs) < 10:
            candidate_clgs.append(challenge_id)
        else:
            candidate_clgs.append(challenge_id) if not random.randint(0,10)>4 else None

    if len(candidate_clgs) > 20: 
        candidate_clgs = candidate_clgs[:10] + random.sample(candidate_clgs[10:], 10)

    return candidate_clgs


def get_unreacted_posts_from_reacted_challenges(user_id:int) -> set:

    candidate_clgs = get_reacted_challenges(user_id)

    postPool = set()
    
    for challenge_id in candidate_clgs:

        n = r.llen(f'clg{challenge_id}posts')
        if n == 0: continue

        postPool = postPool.union(filter_posts(
                        new_posts=random.sample(r.lrange(f'clg{challenge_id}posts',0,-1), min(int(n/10)+1, 10)),
                        existing_posts=getRedisValue(f'{user_id}_reacted_post_pool',onError=set()))        
                    )

    return postPool

def get_unreacted_posts_from_top3Categories(user_id:int, top3) -> set:
    postPool = set()

    for category_code in top3:

        # get all recent post from specified category
        raw_post_pool = r.zrangebyscore(f'category{category_code}post', 0, float('inf'))
        raw_post_pool = [int(post) for post in raw_post_pool]
        n = len(raw_post_pool) 
        if n == 0: continue 
        
        postPool =  postPool.union(filter_posts(
                        new_posts=random.sample(raw_post_pool, min( int(n*0.2 + 1) , 50 )),
                        existing_posts=getRedisValue(f'{user_id}_reacted_post_pool', onError=set()))
                    )
    
    return postPool

def get_popular_posts():
    """
    this function get recent popular posts from PostReaction database. 
    """
    # step 1: skip rows
    k = getRedisValue('postReaction',ranges=[0,0], onError=0, r=r)
    recentPosts = session.query(models.PostReaction).offset(k).subquery()

    # step 2: group by post_id, sum the count column, order by popularity
    post_by_popularity = session.query(
                                recentPosts.c.post_id, 
                                func.sum(recentPosts.c.count).label('total_count')
                            ).group_by(recentPosts.c.post_id
                            ).order_by(desc('total_count'))

    # step 3: limit to the first 500 records (or less if there are fewer rows)
    #         then filter for unreacted posts
    return [instance.post_id for instance in post_by_popularity.limit(500).all()]

def get_unreacted_popular_posts(user_id:int, n:int):
    postPool = set()
    popular_posts = get_popular_posts()
    postPool = postPool.union(filter_posts(
                    new_posts=popular_posts,
                    existing_posts=getRedisValue(f'{user_id}_reacted_post_pool', onError=set()))
                )
    return set(random.sample(list(postPool), min(n, len(postPool))))


def filter_posts(new_posts, existing_posts):
    
    if type(new_posts) != set:
        new_posts = set(new_posts)
    if not existing_posts: return new_posts

    if type(existing_posts) != set:
        existing_posts = set(existing_posts) 
    return new_posts.difference(existing_posts)


def get_recommended_post(user_id):

    postPool = set()

    # get posts from top 3 categories
    top3 = top3categories(user_id)
    if len(top3):
        postPool = postPool.union(get_unreacted_posts_from_top3Categories(user_id,top3))

    # get new posts from user reacted challenges
    postPool = postPool.union(get_unreacted_posts_from_reacted_challenges(user_id))

    # get recent posts that are popular in general 
    postPool = postPool.union(get_unreacted_popular_posts(user_id, min(30, 100-len(postPool))))

    return postPool


if __name__ == "__main__":


    # connect to data base 
    load_dotenv()
    SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}@{os.environ['DATABASE_HOST']}/{os.environ['DATABASE_NAME']}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)  
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()



    ##### test start #####


    def group_testing(userGroup, group_desc):
        print('\n')
        print(f'# ------ {group_desc} ------')

        for user_id in userGroup:
            print('\n')

            print(f'user_id: {user_id}')
            top3 = top3categories(user_id)
            print(f'top3: {top3}')

            post_from_category = get_unreacted_posts_from_top3Categories(user_id,top3)
            print(f'post from category:{post_from_category}')

            post_from_reaction = get_unreacted_posts_from_reacted_challenges(user_id)
            print(f'post from reaction:{post_from_reaction}')

            post_by_popularity = get_unreacted_popular_posts(user_id, n = 5)
            print(f'the popualr posts: {post_by_popularity}')

            print(f'recommended posts --> {get_recommended_post(user_id)}')

    groups = [
        ([-1,-2,-3],'cold start'),
        ([10000,10001,10002], 'user with some challenge'),
        ([1,2,3,4,5], 'users with reaction data')
        ]

    for members, group_description in groups:
        group_testing(members, group_description)



    
    ##### test finished #####
    
    session.close()


