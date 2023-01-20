from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('product/<int:pk>/<str:slug>/', views.PorductDetailView.as_view(), name='product-detail'),
    path('review/<int:pk>/', views.review, name='review'),
]
