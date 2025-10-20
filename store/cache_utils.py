import json
import random

from django.core.cache import cache


CACHE_TTL = 300
RANDOM_OFFSET = 100

def set_cache(key, value,tll=None):
    if tll is None:
        tll = CACHE_TTL + random.randint(-RANDOM_OFFSET, RANDOM_OFFSET)

    ttl = max(1, tll)
    cache.set(key, json.dumps(value), ttl)