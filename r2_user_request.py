import redis
import random 
from r1_automation import decoding, MAX_POST_AGE

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
        challenge_id = int(decoding(reacted_clgs[i]))

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
                postPool.add(int(decoding(item)))

    return postPool


def filteredPosts_from_top3Categories(user_id:int) -> set:
    top3 = top3categories(user_id)
    postPool = set()

    for category_code in top3:

        # get all recent post from specified category
        raw_post_pool = r.zrangebyscore(f'category{category_code}', 0, float('inf'))
        raw_post_pool = [int(post) for post in raw_post_pool]
        n = len(raw_post_pool) 
        if n > 0:
            raw_post_pool = random.sample(raw_post_pool, min( int(n*0.2 + 1) , 100 )  )
                                          
        for post_id in raw_post_pool: 
            if not r.sismember(f'{user_id}_reacted_post_pool', post_id): postPool.add(post_id)
    
    return postPool


def get_recommended_post(user_id):
    post_from_reaction = filteredPosts_from_reacted_challenges(user_id)
    post_from_category = filteredPosts_from_top3Categories(user_id)
    return post_from_reaction.union(post_from_category)


if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379, db=0)

    for user_id in range(1,11):
        print('\n')
        print(f'userid: {user_id}')
        print(f'top3 category = {top3categories(user_id)}')

        post_by_category = filteredPosts_from_top3Categories(user_id)
        post_by_reaction = filteredPosts_from_reacted_challenges(user_id)
        print(f'post by category:\n{post_by_category}\n')
        print(f'post by reaction:\n{post_by_reaction}\n')

        # posts = get_recommended_post(user_id)
        # print(posts)