from django.contrib import admin
from .models import (
    Size,
    Color,
    Category,
    Product,
    ProductImage,
    Campaign,
    Review
)

admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Category)
admin.site.register(Campaign)
admin.site.register(ProductImage)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ['image', 'image_tag', 'order']
    readonly_fields = ['image_tag']
    extra=1
    
class ReviewInline(admin.TabularInline):
    model = Review
    extra=1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # fields = '__all__'
    readonly_fields = ['id', 'slug', 'created']
    inlines = [ProductImageInline, ReviewInline]
