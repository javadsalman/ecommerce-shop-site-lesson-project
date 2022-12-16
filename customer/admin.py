from django.contrib import admin
from .models import (
    Customer,
    Wish,
    BascetItem,
    Order,
    Contact,
)

# Register your models here.

admin.site.register(Customer)
admin.site.register(Wish)
admin.site.register(BascetItem)
admin.site.register(Order)
admin.site.register(Contact)