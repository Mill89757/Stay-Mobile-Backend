# main.py
import json
import redis
from recommendation import *
from datetime import datetime, timedelta
import random
import pandas as pd


# 连接到Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 定义函数以自动化键名的生成
def generate_key(prefix, user_id):
    return f"{prefix}:{user_id}"

# 模拟一个用户列表
user_ids = [f"user{i}" for i in range(10001)]  # 生成10000个用户ID

# 模拟数据格式
posts_data = {
    "post_id": range(1, 51),
    "category_id": [random.randint(0, 4) for _ in range(50)],
    "reaction_count": [random.randint(0, 100) for _ in range(50)],
}
posts_df = pd.DataFrame(posts_data)


# 初始化用户反应记录
user_reactions_record = {user_id: {} for user_id in user_ids}

# 模拟每日操作并将结果存储到Redis中
def daily_recommendation_and_storage(posts_df, user_reactions_record):

    # 确保每个用户在 user_reactions_record 中都有初始记录
    for user_id in user_ids:
        if user_id not in user_reactions_record:
            user_reactions_record[user_id] = {}

    # 用于存储每个用户的操作结果
    operation_results = {}

    for user_id in user_ids:
        # 模拟每日操作
        recommendations, updated_user_reactions_record = simulate_daily_operations_with_specific_user_ids(posts_df, user_reactions_record, "2023-12-12")
        
        # 存储推荐列表到Redis
        rec_key = generate_key("recommendations", user_id)
        rec_result = r.set(rec_key, json.dumps(recommendations[user_id]))
        
        # 存储用户反应记录到Redis
        react_key = generate_key("reactions", user_id)
        react_result = r.set(react_key, json.dumps(updated_user_reactions_record[user_id]))
        r.expire(react_key, timedelta(days=7))  # 设置7天过期

        # 记录操作结果
        operation_results[user_id] = {
            'recommendations_stored': rec_result,
            'reactions_stored': react_result
        }

    return operation_results

# 调用函数执行每日推荐和存储
daily_recommendation_and_storage(posts_df, user_reactions_record)
