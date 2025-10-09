import status as status
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product, OrderItem, Order, Customer, Collection
from .serializers import ProductSerializer, CollectionSerializer


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
            'customer').prefetch_related('orderitem_set').order_by('-placed_at')[:5]
    except ObjectDoesNotExist:
        return Response({'message': '暂未上架'}, status=404)


@api_view(['GET', 'POST'])
def product(request):
    if request.method == 'GET':
        queryset = Product.objects.select_related('collection').all()[:10]
        serializer = ProductSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        if product.orderitem_set.count() > 0:
            return Response(
                {
                    'error': 'Product cannot be deleted because it is associated with an order item.'
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collection(request):
    if request.method == 'GET':
        queryset = Collection.objects.annotate(
            products_count=Count('product')).all()[:10]
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(
        Collection.objects.annotate(
            product_count=Count('product')
        ), pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(instance=collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
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

