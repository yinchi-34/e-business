from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views
from .views import get_ads

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'carts', views.CartViewSet, basename='carts')
router.register(r'ads', views.AdverisementViewSet, basename='ads')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart_items-detail')

ads_router = routers.NestedDefaultRouter(router, 'ads', lookup='ad')

urlpatterns = [
    path('api/ads/', get_ads, name='ads-api'),
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(cart_router.urls)),
    path('', include(ads_router.urls)),
    path('collections/', views.CollectionList.as_view()),
    path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection_detail'),
]
