from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.product, name='product'),
    path('product/<int:id>/', views.product_detail),
    path('collection/', views.collection),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail')
]