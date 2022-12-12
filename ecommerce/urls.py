from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product-list'),
    path('product/<int:pk>/<str:slug>/', views.product_detail, name='product-detail'),
]
