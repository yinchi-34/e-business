from celery import shared_task

from .models import Advertisement
from .cache_utils import set_cache

@shared_task
def refresh_ads_cache(position='homepage'):
    key = f"ads:{position}"
    ads = list(
        Advertisement.objects.filter(position=position, is_active=True)
                     .values('id', 'title', 'image', 'link', 'priority')
                     .order_by('-priority', '-updated_at')
    )

    set_cache(key, ads)
    return ads