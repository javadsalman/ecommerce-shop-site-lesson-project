from django.contrib import sitemaps
from django.urls import reverse
from ecommerce.models import Product

class StaticViewSitemap(sitemaps.Sitemap):
    
    priorities = {
        'ecommerce:home': 1,
        'ecommerce:product-list': 0.4,
        'customer:contact': 0.6
    }
    
    changefreqs = {
        'ecommerce:home': 'daily',
        'ecommerce:product-list': 'always',
        'customer:contact': 'never'
    }
    

    def items(self):
        return [
            'ecommerce:home',
            'ecommerce:product-list',
            'customer:contact',
        ]

    def location(self, item):
        return reverse(item)
    
    def priority(self, item):
        return self.priorities.get(item)
    
    def changefreq(self, item):
        return self.changefreqs.get(item)
    
    
class ProductSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 0.9
    
    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created