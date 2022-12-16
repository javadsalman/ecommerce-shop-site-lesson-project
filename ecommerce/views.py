from django.shortcuts import render, get_object_or_404
from .models import (
    Product, Category, Campaign
)

# Create your views here.

def home(request):
    
    context = {
        'slide_campaigns': Campaign.objects.filter(slide=True),
        'campaigns': Campaign.objects.exclude(slide=True),
        'categories': Category.objects.all()[:12],
        'featured_products': Product.objects.filter(featured=True).order_by('?')[:8],
        'recent_products': Product.objects.all().order_by('-created')[:8]
    }
    return render(request, 'home.html', context=context)

def product_list(request):
    return render(request, 'product-list.html')

def product_detail(request, pk, slug):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'product-detail.html', context=context,)