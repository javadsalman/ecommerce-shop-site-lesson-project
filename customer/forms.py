from django import forms
from django.contrib.auth.models import User
from .models import  (
    Customer, 
    Contact, 
    Order, 
    Purchase, 
    OrderCoupon,
    BascetItem
)
from django.core.mail import send_mail
from .models import PasswordReset
from django.conf import settings


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', }))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', }))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', }))
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control', }))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'class': 'form-control', }))
    password2 = forms.CharField(max_length=50, label='Password Again', widget=forms.PasswordInput(attrs={'class': 'form-control', }))
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            raise forms.ValidationError('Sifreler eyni deyil!')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu email movcuddur!')
        return email
    
    def save(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        new_user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        return new_user
    
    
class ContactForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name', 'class': 'form-control'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Message', 'class': 'form-control', 'rows': '8'}),
        }
        
        
        
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['customer', 'accepted', 'canceled', 'delivered', 'total_price']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'city': forms.Select(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),
        }
        
    def save(self, customer, total_price, coupon, coupon_valid, coupon_price):
        cleaned_data = self.cleaned_data
        
        order = Order.objects.create(
            customer = customer,
            first_name = cleaned_data.get('first_name'),
            last_name = cleaned_data.get('last_name'),
            email = cleaned_data.get('email'),
            address = cleaned_data.get('address'),
            city = cleaned_data.get('city'),
            phone = cleaned_data.get('phone'),
            zipcode = cleaned_data.get('zipcode'),
            total_price = coupon_price if coupon_valid else total_price
        )
        
        if coupon_valid:
            OrderCoupon.objects.create(
                order = order,
                coupon = coupon,
                coupon_code = coupon.code,
                coupon_discount = coupon.discount_percent
            )
            coupon.used_customers.add(customer)
            
        # Create purchases from bascet items at same time by using bulk_create
        purchases = []
        bascet = customer.bascetitem_set.all()
        for bi in bascet:
            purchase = Purchase(
                order=order,
                size=bi.size.title,
                color=bi.color.title,
                price=bi.product.price,
                quantity=bi.quantity,
                title=bi.product.title,
                product=bi.product,
                all_price=bi.product.price * bi.quantity
            )
            purchases.append(purchase)
        Purchase.objects.bulk_create(purchases)
        
        # Delete bascet items after creating purchases
        bascet.delete()
        return order
    
    
class ResetPasswordEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get('email')
        if email and not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bele bir istifadeci yoxdur!')
        return email
        
    def send_reset_mail(self, request):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get('email')
        user = User.objects.get(email=email)
        # create password reset object for user
        password_reset = PasswordReset.objects.create(user=user)
        # generate url for password reset
        url = request.build_absolute_uri(password_reset.get_absolute_url())

        # send email to user
        try:
            send_mail(
                'Multi Shop Reset Password',
                f'Please go to the this page to reset your password: {url}',
                settings.EMAIL_HOST_USER,
                [email],
            )
            return True
        except Exception as message:
            return False
        
class ResetPasswordForm(forms.Form):
    password = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_again = forms.CharField(label='New Password Again', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        password = cleaned_data.get('password')
        password_again = cleaned_data.get('password_again')
        
        if password and password_again and password != password_again:
            raise forms.ValidationError('Sifreler eyni deyil!')
        
    def change_password(self, password_reset):
        password = self.cleaned_data.get('password')
        user = password_reset.user
        user.set_password(password)
        user.save()
        # set used to True for password reset object to prevent using it again
        password_reset.used = True
        password_reset.save()