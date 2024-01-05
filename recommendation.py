import pandas as pd
import random
from datetime import datetime, timedelta

# simulate data
posts_data = {
    "post_id": range(1, 51),
    "category_id": [random.randint(0, 4) for _ in range(50)],
    "reaction_count": [random.randint(0, 100) for _ in range(50)],
}
posts_df = pd.DataFrame(posts_data)


## user dictionary for reaction reacord
user_reactions_record = {
    "123": {},
    "456": {}
}
#后续加个loop给每个user都创建dictionary

def update_unreacted_posts_pool_for_all_users(unreacted_posts_pool, user_reactions_record, current_date):
    updated_unreacted_posts_pool = unreacted_posts_pool.copy()
    for user_id, reactions_by_date in user_reactions_record.items():
        reacted_post_ids = set()
        for date, reactions in reactions_by_date.items():
            if (datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(date, "%Y-%m-%d")).days <= 7:
                reacted_post_ids.update([post_id for post_id, _ in reactions])
        updated_unreacted_posts_pool = updated_unreacted_posts_pool[~updated_unreacted_posts_pool['post_id'].isin(reacted_post_ids)]
    return updated_unreacted_posts_pool

def recommend_posts_for_all_users(unreacted_posts_pool, user_reactions_record, current_date):
    user_recommendations = {}
    for user_id in user_reactions_record.keys():
        recommended_post_ids = unreacted_posts_pool['post_id'].sample(min(10, len(unreacted_posts_pool))).tolist()
        random.shuffle(recommended_post_ids)
        user_recommendations[user_id] = recommended_post_ids
    return user_recommendations

def record_user_reaction(user_id, post_id, reaction_type, date, user_reactions_record):
    if user_id not in user_reactions_record:
        user_reactions_record[user_id] = {}
    if date not in user_reactions_record[user_id]:
        user_reactions_record[user_id][date] = []
    user_reactions_record[user_id][date].append((post_id, reaction_type))


# def simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, current_date):
#     unreacted_posts_pool = update_unreacted_posts_pool_for_all_users(posts_df, user_reactions_record, current_date)
#     user_recommendations = recommend_posts_for_all_users(unreacted_posts_pool, user_reactions_record, current_date)
#     for user_id, recommendations in user_recommendations.items():
#         # 模拟用户对前几个推荐帖子的反应并记录
#         for post_id in recommendations[:3]:  # 假设用户对前3个推荐帖子有反应
#             reaction_type = random.choice(['like', 'comment'])  # 随机选择反应类型
#             record_user_reaction(user_id, post_id, reaction_type, current_date, user_reactions_record)
#     return user_recommendations, user_reactions_record
    
def simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, current_date):
    unreacted_posts_pool = update_unreacted_posts_pool_for_all_users(posts_df, user_reactions_record, current_date)
    user_recommendations = recommend_posts_for_all_users(unreacted_posts_pool, user_reactions_record, current_date)
    for user_id, recommendations in user_recommendations.items():
        for post_id in recommendations[:3]:
            reaction_type = random.choice(['like', 'comment'])
            record_user_reaction(user_id, post_id, reaction_type, current_date, user_reactions_record)  # 确保这里作为参数传入
    return user_recommendations, user_reactions_record

day1 = simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, "2023-12-09")
day2 = simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, "2023-12-10")
day3 = simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, "2023-12-11")

print(day1, day2, day3)


