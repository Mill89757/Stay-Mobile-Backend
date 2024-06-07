# redis_client.py
import redis
import os
# Check if running on EC2
is_running_on_EC2 = True if os.environ.get("AWS_DEFAULT_REGION") else False
if is_running_on_EC2:
    # set up redis for EC2
    redis_endpoint = "stay-mobile-rdb.4weyjt.ng.0001.apse2.cache.amazonaws.com"
    
else:
    # set up redis for local development
    redis_endpoint = "localhost"

# 创建一个 Redis 客户端实例(Create a Redis client instance)
redis_client = redis.StrictRedis(host=redis_endpoint, port=6379, db=0)


