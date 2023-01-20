from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from secrets import token_urlsafe
from uuid import uuid4
from django.urls import reverse
# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.get_full_name()



class Wish(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey('ecommerce.Product', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.customer} - {self.product}'
    
    
class BascetItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey('ecommerce.Product', on_delete=models.CASCADE)
    size = models.ForeignKey('ecommerce.Size', on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey('ecommerce.Color', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.customer} - {self.product} - {self.quantity}'


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    discount_percent = models.FloatField()
    expire = models.DateField()
    used_customers = models.ManyToManyField(Customer, blank=True, related_name='used_coupons')
    
    def is_valid(self, customer):
        return self.expire > timezone.localdate() and not customer in self.used_customers.all()
    
    def __str__(self):
        return self.code

CITY_CHOICES = [
    ('baku', 'Baki'),
    ('kurdamir', 'Kurdemir'),
    ('samakhi', 'Samaxi'),
]
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name='Ad *')
    last_name = models.CharField(max_length=50, verbose_name='Soyad *')
    email = models.EmailField(max_length=50, verbose_name='Email *')
    address = models.CharField(max_length=200, verbose_name='Address *')
    city = models.CharField(choices=CITY_CHOICES, max_length=50, verbose_name='Şəhər *')
    phone = models.CharField(max_length=20, verbose_name='Telefon Nömrəsi *')
    zipcode = models.CharField(max_length=10, verbose_name='Poçt Ünvanı *')
    created = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    total_price = models.FloatField()

    def __str__(self):
        return f'{self.customer}'
    
class OrderCoupon(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='coupon')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code = models.CharField(max_length=20, null=True, blank=True)
    coupon_discount = models.FloatField(max_length=20, null=True, blank=True)
    
class Purchase(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    size = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.IntegerField()
    title = models.CharField(max_length=100)
    product = models.ForeignKey('ecommerce.Product', on_delete=models.SET_NULL, null=True)
    all_price = models.FloatField()

    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expiry = models.DateField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid4, null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.expiry = timezone.localdate() + timedelta(days=1)
        self.token = token_urlsafe(100)
        super().save(*args, **kwargs)
        
    def is_valid(self, token):
        return not self.used and self.expiry > timezone.localdate() and self.token == token
    
    def get_absolute_url(self):
        return reverse('customer:reset-password', kwargs={'uuid': str(self.uuid), 'token': self.token})
    
    
class BulkMail(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    customers = models.ManyToManyField(Customer)
    created = models.DateField(auto_now_add=True)