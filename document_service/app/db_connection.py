import os

from redis import Redis

redis_con = Redis(host=os.environ['REDIS_HOST'])
