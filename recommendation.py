import pandas as pd
import random
from datetime import datetime, timedelta
import pytz
import redis


# connect to redis
r = redis.Redis(host='localhost', port=6379, db=0)

# simulate a user_id list for 10000 users
user_ids = [f"user{i}" for i in range(10001)]

# simulate data
posts_data = {
    "post_id": range(1, 101),
    "category_id": [random.randint(0, 4) for _ in range(100)],
    "reaction_count": [random.randint(0, 100) for _ in range(100)],
}
posts_df = pd.DataFrame(posts_data)


# simulate post_ids
post_ids = list(range(1, 11))

# imulate user reactions
user_reactions_record = {
    'user1': {'post_ids': [1, 2], 'reaction_date': '09-12-2023'},
    'user2': {'post_ids': [2, 3], 'reaction_date': '09-12-2023'},
    'user3': {'post_ids': [4, 5], 'reaction_date': '09-12-2023'}
}




# def update_unreacted_posts_pool_for_all_users(unreacted_posts_pool, user_reactions_record, current_date_str):
#     sydney_timezone = pytz.timezone('Australia/Sydney')
#     # check current_data_str data type
#     if isinstance(current_date_str, str):
#         # if str->datetime
#         current_date = sydney_timezone.localize(datetime.strptime(current_date_str, "%d-%m-%Y"))
#     else:
        
#         current_date = current_date_str

#     updated_unreacted_posts_pool = unreacted_posts_pool.copy()
#     for user_id, reactions_by_date in user_reactions_record.items():
#         reacted_post_ids = set()
#         for date_str, reactions in reactions_by_date.items():
#             if isinstance(date_str, str):
#                 date = sydney_timezone.localize(datetime.strptime(date_str, "%d-%m-%Y"))
#             else:
#                 date = date_str
#             if (current_date - date).days <= 7:
#                 reacted_post_ids.update([post_id for post_id, _ in reactions])
        
#         updated_unreacted_posts_pool = updated_unreacted_posts_pool[~updated_unreacted_posts_pool['post_id'].isin(reacted_post_ids)]
    
#     return updated_unreacted_posts_pool

def update_unreacted_posts_pool_for_all_users(posts_df, user_reactions_record, current_date_str):

    """
    Parameters: 'posts_df': A pandas DataFrame containing post data. 
                This DataFrame should include details such as post IDs, categories, reaction counts, etc.
                'user_reactions_record': A dictionary where each key is a user ID, and the value is a dictionary containing the user's reaction history. 
                The reaction history dictionary should have keys like 'post_ids' (list of post IDs the user reacted to) and 'reaction_date' (the date of reaction).

    Purpose: It iterates through each user's reaction history to check if the reaction date is within the last 7 days.
            For posts that have responded within the last 7 days, they are removed from the updated_unreacted_posts_pool.
F           inally, the function returns an updated pool of unreacted posts.
    """
    sydney_timezone = pytz.timezone('Australia/Sydney')

    # Check and convert the current date
    if isinstance(current_date_str, str):
        current_date = sydney_timezone.localize(datetime.strptime(current_date_str, "%d-%m-%Y"))
    else:
        current_date = current_date_str

    updated_unreacted_posts_pool = posts_df.copy()
    for user_id, reactions in user_reactions_record.items():
        date_str = reactions['reaction_date']
        
        # Make sure date_str is a string and then convert the date
        if isinstance(date_str, str):
            reaction_date = sydney_timezone.localize(datetime.strptime(date_str, "%d-%m-%Y"))
            
            # Compare dates, and if the reaction date is within the last 7 days, the related post is removed from the unreacted post pool
            if (current_date - reaction_date).days <= 7:
                reacted_post_ids = reactions['post_ids']
                updated_unreacted_posts_pool = updated_unreacted_posts_pool[~updated_unreacted_posts_pool['post_id'].isin(reacted_post_ids)]

    return updated_unreacted_posts_pool



def recommend_posts_for_all_users(unreacted_posts_pool, user_reactions_record, current_date):
    """
    Purpose: get 50 recommendation post_id for each user in dic
    
    """

    user_recommendations = {}
    for user_id in user_reactions_record.keys():
        recommended_post_ids = unreacted_posts_pool['post_id'].sample(min(50, len(unreacted_posts_pool))).tolist()
        random.shuffle(recommended_post_ids)
        user_recommendations[user_id] = recommended_post_ids
    return user_recommendations

def record_user_reaction(user_id, post_id, reaction_date, user_reactions_record):
    """
    Purpose: use dictionary to record reacion post_ids for each user
    """
    if user_id not in user_reactions_record:
        user_reactions_record[user_id] = {'post_ids': [], 'reaction_date': reaction_date}
    user_reactions_record[user_id]['post_ids'].append(post_id)



    
# def simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, current_date):
#     unreacted_posts_pool = update_unreacted_posts_pool_for_all_users(posts_df, user_reactions_record, current_date)
#     user_recommendations = recommend_posts_for_all_users(unreacted_posts_pool, user_reactions_record, current_date)
#     for user_id, recommendations in user_recommendations.items():
#         for post_id in recommendations[:3]:
#             reaction_type = random.choice(['like', 'comment'])
#             record_user_reaction(user_id, post_id, reaction_type, current_date, user_reactions_record)  # 确保这里作为参数传入
#     return user_recommendations, user_reactions_record

  
def simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, current_date_str):
    """
     Parameters: 'posts_df': A pandas DataFrame containing post data. 
                This DataFrame should include details such as post IDs, categories, reaction counts, etc.

                'user_reactions_record': A dictionary where each key is a user ID, and the value is a dictionary containing the user's reaction history. 
                The reaction history dictionary should have keys like 'post_ids' (list of post IDs the user reacted to) and 'reaction_date' (the date of reaction).

                'current_date_str': A string representing the current date. The date should be in the format "dd-mm-yyyy". 
                The function converts this date into a timezone-aware datetime object considering the Sydney timezone.

    Purpose: The function is designed to simulate daily operations of a post recommendation system. 
        It updates the pool of unreacted posts based on users' reactions, generates personalized post recommendations for each user, 
        and records user reactions to these recommendations.
    
    
    """
    # set time zone
    sydney_timezone = pytz.timezone('Australia/Sydney')
    # current_date = sydney_timezone.localize(datetime.strptime(current_date_str, "%Y-%m-%d"))

    # check data type
    if isinstance(current_date_str, str):
        current_date = sydney_timezone.localize(datetime.strptime(current_date_str, "%d-%m-%Y"))
    else:
        current_date = current_date_str

    unreacted_posts_pool = update_unreacted_posts_pool_for_all_users(posts_df, user_reactions_record, current_date)
    user_recommendations = recommend_posts_for_all_users(unreacted_posts_pool, user_reactions_record, current_date)

    all_user_recommendations = {}
    all_user_reactions = {}

    for user_id in user_reactions_record.keys():
        # record user reactions 
        for post_id in user_recommendations[user_id]:
            record_user_reaction(user_id, post_id, current_date, user_reactions_record)

        # update recommendation list
        all_user_recommendations[user_id] = user_recommendations[user_id]

        # update reaction for uploading on redis
        all_user_reactions[user_id] = user_reactions_record[user_id]

    return all_user_recommendations, all_user_reactions


day1 = simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, "29-12-2023")
day2 = simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, "30-12-2023")
day3 = simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, "31-12-2023")

print(day1,day2,day3)






