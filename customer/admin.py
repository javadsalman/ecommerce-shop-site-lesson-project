from django.contrib import admin
from .models import (
    Customer,
    Wishlist,
    Bascet,
    Order,
)

# Register your models here.

admin.site.register(Customer)
admin.site.register(Wishlist)
admin.site.register(Bascet)
admin.site.register(Order)