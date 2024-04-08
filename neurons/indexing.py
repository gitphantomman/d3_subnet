import redis
import os
import dotenv
dotenv.load_dotenv()
if os.getenv("REDIS_PASSWORD") is None or os.getenv("REDIS_PASSWORD") == "":
    r = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), decode_responses = True, db = 0)
    r1 = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), decode_responses = True, db = 1)
else:
    r = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), decode_responses = True, password= os.getenv("REDIS_PASSWORD"), db = 0)
    r1 = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), decode_responses = True, password= os.getenv("REDIS_PASSWORD"),  db = 1)
def save(key, value):
    r.set(key, value)
def get(key):
    return r.get(key)

def save_temp_indexing(key, value):
    r1.set(key, value)
def get_temp_indexing(key):
    return r1.get(key)
# Delete db1    
def remove_temp_indexing():
    r1.flushdb()
    
# output all key, values of db1
def get_all_temp_indexing_keys():
    return r1.keys()

