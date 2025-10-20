import json
import random


from django.core.cache import cache
from .models import Advertisement


def get_ads_by_position(position='homepage'):
    key = f'ads:{position}'
    data = cache.get(key)

    if data:
        return json.loads(data)

    ads = list(Advertisement.objects.filter(position=position, is_active=True)
               .values('id', 'title', 'image', 'link'))

    ttl = 300 + random.randint(-100, 100)
    cache.set(key, json.dumps(ads), ttl)
    return ads
