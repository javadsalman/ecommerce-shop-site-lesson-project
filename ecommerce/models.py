from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from imagekit.models.fields import ProcessedImageField
from django.contrib.admin import display
from django.utils.html import format_html
from django.urls import reverse, reverse_lazy
from .utils import convert_slug
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from django.utils.translation import get_language, gettext, gettext_lazy as _


# Create your models here.



class Size(models.Model):
    title = models.CharField(max_length=10)
    
    def __str__(self):
        return self.title
    
    
class Color(models.Model):
    title = models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
  
class Category(models.Model):
    super = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='category_images/')
    title = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def is_super(self):
        return self.category_set.exists()
    
    def get_absolute_url(self):
        return reverse('ecommerce:product-list') + f'?category={self.pk}'
    



class Campaign(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='campaign_images/')
    discount = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(100)], null=True, blank=True)
    slide = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('ecommerce:product-list') + f'?campaigns={self.pk}'
    

class Product(models.Model):
    title_az = models.TextField(max_length=100)
    title_en = models.TextField(max_length=100, null=True, blank=True)
    title_tr = models.TextField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    description = RichTextField()
    old_price = models.FloatField(validators=[MinValueValidator(0.1)], null=True, blank=True)
    price = models.FloatField(validators=[MinValueValidator(0.1)])
    sizes = models.ManyToManyField(Size)
    colors = models.ManyToManyField(Color)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    campaigns = models.ManyToManyField(Campaign, related_name='products', blank=True)
    featured = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    @property
    def title(self):
        lang = get_language()
        title = getattr(self, 'title_' + lang)
        return title or self.title_az
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = convert_slug(self.title_az)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse_lazy('ecommerce:product-detail', kwargs={'pk': self.pk, 'slug': self.slug})

    @property
    def average_star_count(self):
        reviews = self.review_set.all()
        if reviews:
            result =  reviews.aggregate(average=Avg('star_count')).get('average')
        else:
            result = 0
        return result
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = ProcessedImageField(upload_to='products/product-image/', format='JPEG', options={'quality': 70})
    order = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    
    @display(description='Movcud sekil')
    def image_tag(self):
        return format_html(f'<img src={self.image.url} width="250">')

    class Meta:
        ordering = ['order']
    
    
class Review(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, validators=[MaxValueValidator(6), MinValueValidator(1)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    star_count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    
