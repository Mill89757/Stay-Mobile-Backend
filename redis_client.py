# redis_client.py
import redis

# 创建一个 Redis 客户端实例
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

