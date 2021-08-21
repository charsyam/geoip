from utils import get_timestamp


class LocalCache:
    def __init__(self):
        self.cache = {}

    def put(self, key, value, ttl = -1):
        if ttl >= 0:
            ttl = ttl + get_timestamp() 
            
        cache_value = {"value": value, "ttl": ttl}
        self.cache[key] = cache_value
        return True


    def get(self, key):
        if key not in self.cache:
            return None

        cache_value = self.cache[key]
        ttl = cache_value["ttl"]
        expire_time = get_timestamp()

        if ttl >= 0 and ttl < expire_time:
            del self.cache[key]
            return None

        return cache_value["value"]
