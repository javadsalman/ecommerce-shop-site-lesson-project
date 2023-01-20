from django.contrib import admin
from .models import (
    Customer,
    Wish,
    BascetItem,
    Order,
    Contact,
    Purchase,
    Coupon,
    OrderCoupon,
    PasswordReset,
    BulkMail
)

# Register your models here.

admin.site.register(Customer)
admin.site.register(Wish)
admin.site.register(BascetItem)
admin.site.register(Contact)
admin.site.register(Purchase)
admin.site.register(Coupon)
admin.site.register(OrderCoupon)
admin.site.register(PasswordReset)
admin.site.register(BulkMail)



class OrderCouponInline(admin.TabularInline):
    model = OrderCoupon
    extra = 0
class PurchaseInline(admin.StackedInline):
    model = Purchase
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderCouponInline, PurchaseInline]