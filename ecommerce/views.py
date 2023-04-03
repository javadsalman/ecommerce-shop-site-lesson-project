from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Product, Category, Campaign, Color, Size, Review
)
from django.core.paginator import Paginator
from django.db.models import Avg, F, Count, Max, Min
from .filters import ProductFilter
from django.contrib.postgres.search import TrigramWordSimilarity
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView

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


class ProductListView(ListView):
    template_name = 'product-list.html'
    context_object_name = 'products'
    
    def get_paginate_by(self, *args, **kwargs):
        # paginate by page count from query string or default 6
        return int(self.request.GET.get('page_by', 6))
    
    def get_queryset(self, *args, **kwargs):
        sorting = self.request.GET.get('sorting')
        all_products = Product.objects.all()
        # search by trigram similarity of title
        if search:=self.request.GET.get('search'):
            all_products = all_products.annotate(similarity=TrigramWordSimilarity(search, 'title_az'))\
            .filter(similarity__gt=0.3).order_by('-similarity')
            # # search by postgres search vector and make order by rank of search
            # # that title has more weight than description and category and description has more weight than category
            # vector = SearchVector('title_az', weight='A') + SearchVector('description', weight='B') + SearchVector('category__title', weight='C')
            # all_products = all_products.annotate(rank=SearchRank(vector, SearchQuery(search), weights=[0.1, 0.5, 0.7, 0.8])).filter(rank__gte=0.3).order_by('-rank')
        
        filter_result = ProductFilter(self.request.GET, all_products)
        filtered_products = filter_result.qs
        if sorting:
            # Ensure that null values are last by using nulls_last=True
            # For details see https://docs.djangoproject.com/en/4.2/ref/models/expressions/#using-f-to-sort-null-values
            sorting = F(sorting[1:]).desc(nulls_last=True) if sorting[0] == '-' else F(sorting).asc(nulls_last=True)
            filtered_products = filtered_products.annotate(avg_review=Avg('review__star_count')).order_by(sorting)

        return filtered_products
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = context['page_obj']
        context["paginator"] = context['page'].paginator
        context['colors'] = Color.objects.all().annotate(count=Count('product'))
        context['sizes'] = Size.objects.all().annotate(count=Count('product'))
        context['price_info'] = Product.objects.all().aggregate(min_value=Min('price'), max_value=Max('price'))
        return context
    


# def product_list(request):
#     current_page = request.GET.get('page', 1)
#     sorting = request.GET.get('sorting')
#     page_by = int(request.GET.get('page_by', 6))
    
#     all_products = Product.objects.all()
#     if search:=request.GET.get('search'):
#         all_products = all_products.annotate(similarity=TrigramWordSimilarity(search, 'title_az'))\
#         .filter(similarity__gt=0.3).order_by('-similarity')
#         # vector = SearchVector('title_az', weight='A') + SearchVector('description', weight='B') + SearchVector('category__title', weight='C')
#         # all_products = all_products.annotate(rank=SearchRank(vector, SearchQuery(search), weights=[0.1, 0.5, 0.7, 0.8])).filter(rank__gte=0.3).order_by('-rank')
    
    
#     filter_result = ProductFilter(request.GET, all_products)
#     filtered_products = filter_result.qs
#     if sorting:
#         sorting = F(sorting[1:]).desc(nulls_last=True) if sorting[0] == '-' else F(sorting).asc(nulls_last=True)
#         filtered_products = filtered_products.annotate(avg_review=Avg('review__star_count')).order_by(sorting)
        
#     paginator = Paginator(filtered_products, page_by)
#     page = paginator.page(current_page)
#     products = page.object_list
    
#     context = {
#         'page': page,
#         'paginator': paginator,
#         'products': products,
#         'filter_result': filter_result,
#         'colors': Color.objects.all().annotate(count=Count('product')),
#         'sizes': Size.objects.all().annotate(count=Count('product')),
#         'price_info': Product.objects.all().aggregate(min_value=Min('price'), max_value=Max('price')),
#     }
    
#     return render(request, 'product-list.html', context)

class PorductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'product-detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        reviews = product.review_set.all()
        if self.request.user.is_authenticated:
            customer_review = product.review_set.filter(customer=self.request.user.customer).first()
            reviews = reviews.exclude(customer=self.request.user.customer)
        context['reviews'] = reviews
        context['customer_review'] = customer_review
        return context
    
    

# def product_detail(request, pk, slug):
#     product = get_object_or_404(Product, pk=pk)

#     customer_review = None
#     reviews = product.review_set.all()
#     if request.user.is_authenticated:
#         customer_review = product.review_set.filter(customer=request.user.customer).first()
#         reviews = reviews.exclude(customer=request.user.customer)
        
#     context = {
#         'product': product,
#         'customer_review': customer_review,
#         'reviews': reviews,
#     }
    
#     return render(request, 'product-detail.html', context=context,)


@login_required
def review(request, pk):
    if request.method == 'GET':
        return redirect(product.get_absolute_url())
    
    product = get_object_or_404(Product, pk=pk)
    customer = request.user.customer
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save(customer, product)
        
    return redirect(product.get_absolute_url())
    
    
    
    
    
    
