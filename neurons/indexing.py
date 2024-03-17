import redis
r = redis.Redis(host = 'localhost', port = 6379, decode_responses = True)

def save(key, value):
    r.set(key, value)
def get(key):
    return r.get(key)