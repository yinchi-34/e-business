from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from store.models import Product
from tags.models import TaggedItem


def get_product_tag(request):
    contenttype = ContentType.objects.get_for_model(Product)

    queryset = TaggedItem.objects.\
        select_related('tag').\
        filter(
            content_type=contenttype,
            object_id=1,
    )