from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from imagekit.models.fields import ProcessedImageField
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
    title = models.CharField(max_length=20)
    
    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    description = RichTextField()
    price = models.FloatField(validators=[MinValueValidator(0.1)])
    sizes = models.ManyToManyField(Size)
    colors = models.ManyToManyField(Color)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = ProcessedImageField(upload_to='products/product-image/', format='JPEG', options={'quality': 70})
    order = models.IntegerField(validators=[MinValueValidator(1)])
    
    
class Review(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    star_count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created = models.DateTimeField(auto_now_add=True)