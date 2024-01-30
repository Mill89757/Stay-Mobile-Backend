import redis
import random 
from r1_automation import byte_to_utf8, CLG_CATEGORY

def top3categories(user_id:int) -> list:
    """
    the 'user_contribution' key in redis is a hash table that record user's contribution to each challenge category.
    this function takes user_id as input and return 3 categories where the user has spent the most time contributing.
    """
    
    # retrive user's challenge contribution data.

    # contribution = byte_to_utf8( r.hget('user_contribution',user_id), StrToSplit=',')
    # if not contribution: return []
    contribution = byte_to_utf8( r.hget('user_contribution',user_id), StrToSplit=',', ifError=[0]*5)
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




def filteredPosts_from_reacted_challenges(user_id:int) -> set:
    """
    This function takes user_id as input, it then return unreacted posts from selected challenges 
    that the user has recently engaged with. (maximum 200 posts from 20 challenges)
    """

    # get a list of user reacted challenges
    reacted_clgs = r.zrevrange(f'{user_id}_clgs_preference', 0, -1)

    # randomly select a few challenges from reacted_clgs
    candidate_clgs = []

    for i in range(len(reacted_clgs)):
        challenge_id = byte_to_utf8(reacted_clgs[i])

        if i == 30 and len(candidate_clgs)>10:
            random.sample(candidate_clgs, 10)

        # get rid of outdated challenges from redis object {user_id}_clg_preference
        if r.hget('on_clg_info', challenge_id) == None: 
            r.zrem(f'{user_id}_clg_preference',challenge_id)
            continue 

        # randomly pick recent challenges as candidate challenge
        if i < 30:
            candidate_clgs.append(challenge_id)
        else:
            candidate_clgs.append(challenge_id) if not random.randint(0,1) else None

    if len(candidate_clgs) > 20: 
        candidate_clgs = candidate_clgs[:10] + random.sample(candidate_clgs[10:], 10)


    # get posts from candidate challenges
    postPool = set()
    
    for challenge_id in candidate_clgs:

        n = r.llen(f'clg{challenge_id}posts')
        posts = random.sample(r.lrange(f'clg{challenge_id}posts',0,-1), min(int(n/10)+1, 10))
        
        for item in posts:
            if not r.sismember(f'{user_id}_reacted_post_pool', item):
                postPool.add(byte_to_utf8(item))

    return postPool


def filteredPosts_from_top3Categories(user_id:int, top3) -> set:
    postPool = set()

    for category_code in top3:

        # get all recent post from specified category
        raw_post_pool = r.zrangebyscore(f'category{category_code}post', 0, float('inf'))
        raw_post_pool = [int(post) for post in raw_post_pool]
        n = len(raw_post_pool) 
        if n > 0:
            raw_post_pool = random.sample(raw_post_pool, min( int(n*0.2 + 1) , 100 )  )
                                          
        for post_id in raw_post_pool: 
            if not r.sismember(f'{user_id}_reacted_post_pool', post_id): postPool.add(post_id)
    
    return postPool


def get_popular_posts(n):return set()


def get_recommended_post(user_id):

    # get posts from top 3 categories
    top3 = top3categories(user_id)
    if len(top3):
        post_from_category = filteredPosts_from_top3Categories(user_id,top3)

    # get new posts from user reacted challenges
    post_from_reaction = filteredPosts_from_reacted_challenges(user_id)

    # get recent posts that are popular in general 
    if len(top3) == 0:
        popular_posts = get_popular_posts(50)
    else:
        popular_posts = get_popular_posts(20)

    return post_from_reaction.union(post_from_category).union(popular_posts)


if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379, db=0)

    def group_testing(userGroup, group_desc):
        print('\n')
        print(f'# ------ {group_desc} ------')

        for user_id in userGroup:
            print('\n')

            print(f'user_id: {user_id}')
            top3 = top3categories(user_id)
            print(f'top3: {top3}')
            post_from_category = filteredPosts_from_top3Categories(user_id,top3)
            post_from_reaction = filteredPosts_from_reacted_challenges(user_id)
            if len(top3) == 0:
                popular_posts = get_popular_posts(50)
            else:
                popular_posts = get_popular_posts(20)
            print(f'post from category:{post_from_category}')
            print(f'post from reaction:{post_from_reaction}')
            print(f'the popualr posts: {popular_posts}')
            print(f'recommended posts --> {get_recommended_post(user_id)}')

    groups = [
        ([-1,-2,-3],'cold start'),
        ([10000,10001,10002], 'user with some challenge'),
        ([1,2,3,4,5], 'users with reaction data')
        ]

    for members, group_description in groups:
        group_testing(members, group_description)