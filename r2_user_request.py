import redis
import random 
from r1_automation import decoding

def top3categories(user_id:int) -> set:
    """
    the 'user_contribution' key in redis is a hash table that record user's contribution to each challenge category.
    this function takes user_id as input and return 3 categories where the user has spent the most time contributing.
    """
    
    # retrive uer's challenge contribution data.
    contribution = decoding( r.hget('user_contribution',user_id), StrToSplit=',', ifError=['0']*5)
    contribution = [int(num) for num in contribution]

    topCategories = []

    for category in range(5):

        # if user did not contribute to category i, then move on to the next category
        if contribution[category] == 0: continue 

        # otherwise, see if user's contribution is one of the top 3 cateogries. 
        for i in range(len(topCategories)):
            if contribution[category] > contribution[topCategories[i]]: 
                topCategories.insert(i, category)
                continue
        if len(topCategories) < 3: 
            contribution.append(category)
        elif len(topCategories) > 3:
            contribution.pop()

    # if user contributed to less than 3 categories, 
    # then randomly pick some other categories for this user
    n = len(topCategories)
    if n == 3:
        return topCategories
    other_categories = [item for item in [0,1,2,3,4] if item not in topCategories]
    return  topCategories + random.sample(other_categories, 3-n)


def filteredPosts_from_reacted_challenges(user_id:int) -> list:
    """
    user can interact with posts, each post belongs to 1 challenge.
    so reacting to recent post is equivalent to react to a challenge.
    this function allocates new posts to users based on their interacted challenges.
    """
    postPool = []
    recent_posts = r.hkeys('post_clg_pair')
    recent_posts = random.sample(recent_posts, min(len(recent_posts),200))
    top3 = top3categories(user_id)

    for post_id in recent_posts:
        clg_id = r.hget('post_clg_pair', post_id)
        category = int(decoding(r.hget('on_clg_info', clg_id), StrToSplit=',')[0])
        if category not in top3:
            interacted_post = r.sismember(f'{user_id}_liked_posts', post_id)
            interacted_clg = r.zscore(f'{user_id}_clgs_preference',post_id)
            if not interacted_post or interacted_clg:
                postPool.append(int(decoding(post_id)))
    
    return postPool


def filteredPosts_from_top3Categories(user_id:int) -> list:
    top3 = top3categories(user_id)
    postPool = []

    for category_code in top3:

        # get all recent post from specified category
        raw_post_pool = r.zrangebyscore(f'recent_posts_for_category{category_code}', 0, float('inf'))
        raw_post_pool = [int(post) for post in raw_post_pool]
        raw_post_pool = random.sample(raw_post_pool, min(len(raw_post_pool), 100))
        
        for post_id in raw_post_pool: 
            if not r.sismember(f'{user_id}_liked_posts', post_id): postPool.append(post_id)
    
    return postPool


def get_recommended_post(user_id):
    return filteredPosts_from_reacted_challenges(user_id) + filteredPosts_from_top3Categories(user_id)


if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379, db=0)

    for user_id in range(1,11):
        top3 = top3categories(user_id)
        # post_by_category = filteredPosts_from_top3Categories(user_id)
        # post_by_reaction = filteredPosts_from_reacted_challenges(user_id)
        posts = get_recommended_post(user_id)
        print('\n')
        print(f'userid: {user_id}')
        print(f'top3 category = {top3}')
        print(posts)
        # print(f'post by category:\n{post_by_category}\n')
        # print(f'post by reaction:\n{post_by_reaction}\n')
        