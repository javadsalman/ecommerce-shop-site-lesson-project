from django.shortcuts import render, get_object_or_404
from .models import (
    Product
)

# Create your views here.

def home(request):
    return render(request, 'home.html')

def product_list(request):
    return render(request, 'product-list.html')

def product_detail(request, pk, slug):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product
    }
    return render(request, 'product-detail.html', context=context)