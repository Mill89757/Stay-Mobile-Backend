import os

import redis
from dotenv import load_dotenv

load_dotenv()

# Remote server has REDIS_ENDPOINT set in the environment
# Local development uses localhost
REDIS_ENDPOINT = os.environ.get("REDIS_ENDPOINT")

# Create a Redis client instance
r = redis.StrictRedis(host=REDIS_ENDPOINT, port=6379, db=0)
