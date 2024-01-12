from p1_load_data import * 
import models
import datetime 
import pytz
import random 


r = redis.Redis(host='localhost', port=6379, db=0)


sydney_tz = pytz.timezone('Australia/Sydney')
DATE_TODAY = datetime.datetime.now(sydney_tz).date()



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
        if item == ['']: return []
        else: return item 



def classify_new_posts_by_category():
    """
    every post belongs to 1 challenge, every challenge has a category.
    this function match post_id to category code (0,1,2,3,4) through challenge_id.
    """
    post_by_category = [[] for i in range(5)]
    challenge_to_be_removed = []

    for instance in POST:

        # get data for challenge_id, post_id, is_breaking_day

        challenge_id = instance.challenge_id
        post_id = instance.id
        is_breaking_day = False
        if instance.written_text == 'I have a break today.':
            is_breaking_day = True

        # get challenge detail 
        clg_detail = r.hget('on_clg_info', challenge_id)
         
        # add new challenge's detail to on_clg_info 
        if clg_detail == None:
            clg_record = session.query(models.Challenge
                                       ).filter(models.Challenge.id == challenge_id).first()

            # clg_record = [instance.id for instance in clg_record]
            clg_category = clg_record.category
            clg_isPublic = clg_record.is_public
            clg_done_by = clg_record.created_time + datetime.timedelta(days = clg_record.duration)
            clg_done_by = clg_done_by.date().strftime("%Y-%m-%d")

            r.hset('on_clg_info', challenge_id, 
                   f'{clg_category},{clg_isPublic},{clg_done_by}')
            clg_detail = r.hget('on_clg_info', challenge_id)
        
        
        category, isPublic, doneby = decoding(clg_detail, StrToSplit=',')
        category = int(category)
        doneby = datetime.datetime.strptime(doneby[:], '%Y-%m-%d')
        
        # add public, non-break post to the list 
        if isPublic and is_breaking_day==False:
            post_by_category[category].append(str(post_id))

        # check whether we should remove this challenge 
        if doneby == DATE_TODAY:
            challenge_to_be_removed.append(challenge_id)

    # store data to redis
    for category in range(5):
        r.hset('category_posts', category, ','.join(post_by_category[category]) )

    return challenge_to_be_removed

def __record_likerID_under_challengeID():
    """
    users can react to post, each post belong to 1 and only 1 challenge
    this funtion connect user to challenge via the posts they reacted recently (past 5 days).
    """

    for instance in LIKE:
        challenge_id = instance.challenge_id
        user_id = instance[0].user_id
        is_cancelled = instance[0].is_cancelled

        clg_detail = r.hget('on_clg_info', challenge_id)
        if not clg_detail: continue
        if is_cancelled: continue


        current_likers = decoding(r.hget('like_record_5', challenge_id), ifError='')

        # initialise challenge like records
        if not current_likers:
            current_likers = ''
            for i in range(1,6):
                r.hset('like_record_'+str(i), challenge_id,'')
            
        r.hset('like_record_5', challenge_id, current_likers+','+ str(user_id))



def update_user_challenge_distribution(): 
    """
    challenge belongs to user. challenge has duration that contribute to category distribution.
    this function iterate through new challenges and update category distribution for users. 
    """
    for instance in CHALLENGE:

        challenge = instance.id
        duration = instance.duration
        category = instance.category
        members = session.query(models.GroupChallengeMembers
                    ).filter(models.GroupChallengeMembers.challenge_id == challenge
                    ).all()
        members = [instance.user_id for instance in members]


        for user in members:

            # get user's current contribution
            contribution = decoding(r.hget('user_contribution',user), StrToSplit=',', ifError=['0']*5)

            # modify user contribution according to the challenge's category
            contribution[category] = str( int(contribution[category]) + duration)
            contribution = ','.join(contribution)
            
            # update change to redis 
            r.hset('user_contribution', user, contribution)

    
def recommend_post_from_interacted_challenges():
    """
    user can interact with posts, each post belongs to 1 challenge.
    so reacting to recent post is equivalent to react to a challenge.
    this function allocates new posts to users based on their interacted challenges.
    """

    # match new reaction records to challenges through posts
    __record_likerID_under_challengeID()


    # for each new post, find it's challenge, then allocates it to 
    # users who recently reacted to that challenge

    tmp_data = dict()   # { user: post_he/she_might_be_interested }

    for instance in POST:
        clg_id = instance.challenge_id
        post_id = instance.id

        # iterate through like_record_[1~5]
        for day in range(1,6):
            record_day = 'like_record_' + str(day)

            users = decoding( r.hget(record_day, clg_id), StrToSplit=',' , ifError=[] )

            # allocate post_id to all users in like_record_[day]
            for user in users:
                if user not in tmp_data:
                    tmp_data[user] = {post_id}
                else:
                    tmp_data[user].add(post_id)

    # saving the results to redis 
    for user in tmp_data.keys():
        # posts = ','.join(list(tmp_data[str(user)]))
        posts = ','.join(str(item) for item in list(tmp_data[user]))
        # print(posts)
        r.hset('user_like', user, posts)
    

def top3categories(user_id:int) -> list:
    """
    the 'user_contribution' key in redis is a hash table that record user's contribution to each challenge category.
    this function takes user_id as input and return 3 categories where the user has spent the most time contributing.
    """
    
    # retrive his/her challenge contribution data.
    contribution = decoding( r.hget('user_contribution',user_id), StrToSplit=',', ifError=[])
    if contribution:
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
        return top3categories
    other_categories = [item for item in [0,1,2,3,4] if item not in topCategories]
    return  topCategories + random.sample(other_categories, 3-n)


def get_recommended_post(user_id) -> list:
    """
    recommended posts might come from users' interaction and the distribution of user's own challenge category.
    this function takes an user_id as input and return a list of post_id for recommendation. 
    """
    posts = set()

    post_by_reactions = decoding(r.hget('user_like', user_id), StrToSplit=',', ifError=[])

    if post_by_reactions:  
        post_by_reactions = [int(post) for post in post_by_reactions]
        posts = set(post_by_reactions)

    suggested_categories = top3categories(user_id)
    for category_code in suggested_categories:
        category_posts = r.hget('category_posts', category_code)
        
        if not category_posts: continue
        category_posts = decoding(category_posts,StrToSplit=',')
        if not category_posts: continue

        for post_id in category_posts:
            posts.add(int(post_id))

    return suggested_categories, list(posts)

