from django.contrib import admin
from .models import (
    Size,
    Color,
    Category,
    Product,
    ProductImage,
)

admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)