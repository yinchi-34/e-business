from django.db.models import Count, F
from django.db.models.aggregates import Sum
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .utils import get_ads_by_position
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework import status, viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .filter import ProductFilter
from .models import Product, OrderItem, Order, Customer, Collection, Cart, CartItem, Advertisement
from .serializers import ProductSerializer, CollectionSerializer, CartSerializer, CartItemSerializer, \
    AdvertisementSerializer
from .task import refresh_ads_cache


def get_order_product(request):
    try:
        '''
        所有订单中的货物通过title排序
        1.获取OrderItem的产品id并且去重
        2.从产品列表返回product
        '''
        queryset = Product.objects.filter(
            id__in=OrderItem.objects.values('product_id').distinct())
    except ObjectDoesNotExist:
        return Response({'message': '暂未上架'}, status=404)


def get_order(request):
    try:
        queryset = Order.objects.select_related(
            'customer').prefetch_related('orderitem_set').order_by('-placed_at')
    except ObjectDoesNotExist:
        return Response({'message': '暂未上架'}, status=404)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() > 0:
            return Response(
                {
                    'error': 'Product cannot be deleted because it is associated with an order item.'
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(
            products_count=Count('product')).all()[:10]
    serializer_class = CollectionSerializer


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(product_count=Count('product'))
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        #queryset返回的是queryset多个对象，没有调用get_object，不是单个对象
        collection = self.get_object()
        product_count = collection.product_set.count()
        if product_count > 0 and not request.GET.get('confirm'):
            return Response(
                {
                    'message': f'该集合下包含{product_count}个产品，删除同时将移除这些产品！',
                    'confirm_required': True
                },
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            collection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        # 该查询触发了三个表，购物车，购物车清单，产品清单，所以prefetch应该加入product，否则会出现cartitem__productN+1查询
        return Cart.objects.prefetch_related('items__product').annotate(
            total_price=Sum(F('items__product__price') * F('items__quantity')), )


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


@api_view(['GET'])
def get_ads(request):
    position = request.GET.get('position', 'homepage')
    ads = get_ads_by_position(position)

    # 异步刷新缓存（非阻塞）
    refresh_ads_cache.delay(position)

    return Response({'position': position, 'ads': ads})

class AdverisementViewSet(ModelViewSet):
    serializer_class = AdvertisementSerializer
    queryset = Advertisement.objects.filter(position='position')
