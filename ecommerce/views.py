from django.shortcuts import render, get_object_or_404
from .models import (
    Product, Category, Campaign
)
from django.core.paginator import Paginator
from django.db.models import Avg, F


# Create your views here.

def home(request):
    
    context = {
        'slide_campaigns': Campaign.objects.filter(slide=True),
        'campaigns': Campaign.objects.exclude(slide=True),
        'categories': Category.objects.all()[:12],
        'featured_products': Product.objects.filter(featured=True).order_by('?')[:8],
        'recent_products': Product.objects.all().order_by(F('created').desc())[:8]
    }
    return render(request, 'home.html', context=context)

def product_list(request):
    current_page = request.GET.get('page', 1)
    sorting = request.GET.get('sorting', '-created')
    sorting = F(sorting[1:]).desc(nulls_last=True) if sorting[0] == '-' else F(sorting).asc(nulls_last=True)
    page_by = int(request.GET.get('page_by', 6))
    
    all_products = Product.objects.all().annotate(avg_review=Avg('review__star_count')).order_by(sorting)
    paginator = Paginator(all_products, page_by)
    page = paginator.page(current_page)
    products = page.object_list
    
    context = {
        'page': page,
        'paginator': paginator,
        'products': products,
    }
    
    return render(request, 'product-list.html', context)

def product_detail(request, pk, slug):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'product-detail.html', context=context,)