from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.get_full_name()
    
    # def __repr__(self):
    #     return self.user.get_full_name()


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey('ecommerce.Product', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.customer} - {self.product}'
    
    
class Bascet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey('ecommerce.Product', on_delete=models.CASCADE)
    size = models.ForeignKey('ecommerce.Size', on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey('ecommerce.Color', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer} - {self.product} - {self.quantity}'


CITY_CHOICES = [
    ('baku', 'Baki'),
    ('kurdamir', 'Kurdemir'),
    ('samakhi', 'Samaxi'),
]
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    city = models.CharField(choices=CITY_CHOICES, max_length=50)
    zipcode = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.customer}'

    

    