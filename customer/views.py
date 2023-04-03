from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    RegisterForm, ContactForm, CheckoutForm, ResetPasswordEmailForm, ResetPasswordForm
)
from django.contrib.auth import login, logout, authenticate
from ecommerce.models import Product
from .models import (
    Customer, Wish, BascetItem, Order, Coupon, PasswordReset
)
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.views.generic import TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect
import requests, os

RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

# Create your views here.

class ContactView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'contact.html', context={'form': form})
    
    def post(self, request):
        form = ContactForm(data=request.POST)
        # check recaptcha validation
        response = requests.post(' https://www.google.com/recaptcha/api/siteverify', {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': request.POST.get('g-recaptcha-response')
        })
        recaptcha_result = response.json()
        success = recaptcha_result.get('success')
        score = recaptcha_result.get('score')
        # if form is valid and recaptcha is valid and score is greater than 0.7 then save form
        if form.is_valid() and success and score > 0.7:
            form.save()
            return render(request, 'contact.html', context={'form': ContactForm(), 'status': 'success'})
        return render(request, 'contact.html', context={'form': form, 'status': 'fail'})

# def contact(request):
#     form = ContactForm()
#     if request.method == 'POST':
#         form = ContactForm(data=request.POST)
#         response = requests.post(' https://www.google.com/recaptcha/api/siteverify', {
#             'secret': RECAPTCHA_SECRET_KEY,
#             'response': request.POST.get('g-recaptcha-response')
#         })
#         recaptcha_result = response.json()
#         success = recaptcha_result.get('success')
#         score = recaptcha_result.get('score')
#         if form.is_valid() and success and score > 0.7:
#             form.save()
#             return render(request, 'contact.html', context={'form': ContactForm(), 'status': 'success'})
#         return render(request, 'contact.html', context={'form': form, 'status': 'fail'})
#     return render(request, 'contact.html', context={'form': form})


# use csrf_protect where it is needed
@csrf_protect
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            nextUrl = request.GET.get('next')
            if not remember_me:
                request.session.set_expiry(0)
            return redirect('ecommerce:home')
        return render(request, 'login.html', context={'unsuccess': True})

def logout_view(request):
    logout(request)
    return redirect('customer:login')

@csrf_protect
def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', context={'form': form})
        
    elif request.method == 'POST':
        form = RegisterForm(data=request.POST)
        # the value of the checkbox of terms and conditions is 'on' if it is checked
        accepted = request.POST.get('accepted')
        if form.is_valid() and accepted:
            user = form.save()
            login(request, user)
            return redirect('ecommerce:home')
        # check if user accepted terms and conditions
        elif not accepted:
            return render(request, 'register.html', context={'form': form, 'not_accepted':True})
        else:
            return render(request, 'register.html', context={'form': form})


# @login_required
# def wishlist(request):
#     customer = request.user.customer
#     wishlist = customer.wish_set.all()
#     return render(request, 'wishlist.html', context={'wishlist': wishlist})

class WishlistView(LoginRequiredMixin, ListView):
    context_object_name = 'wishlist'
    template_name = 'wishlist.html'
    # get the current user's wishlist
    def get_queryset(self):
        customer = self.request.user.customer
        return customer.wish_set.all()



@login_required
def add_to_wish(request, pk):
    customer = request.user.customer
    product = Product.objects.get(pk=pk)
    current_wish = Wish.objects.filter(customer=customer, product=product)
    if current_wish:
        current_wish.delete()
    else:
        Wish.objects.create(customer=customer, product=product)
    next_url = request.GET.get('next')
    # wishlist = Wishlist(customer=customer, product=product)
    # wishlist.save()
    return redirect(next_url)


@login_required
def remove_wish(request, pk):
    wish = get_object_or_404(Wish, pk=pk)
    wish.delete()
    return redirect('customer:wishlist')

@login_required
def add_to_bascet(request, pk):
    if request.method == 'POST':
        customer = request.user.customer
        product = get_object_or_404(Product, pk=pk)
        size = request.POST.get('size')
        color = request.POST.get('color')
        quantity = request.POST.get('quantity')
        BascetItem.objects.create(
            customer=customer, product=product,
            size_id=size, color_id=color, quantity=quantity
        )
        return redirect('customer:bascet')
    else:
        return redirect('ecommerce:home')


@login_required
@csrf_protect
def bascet(request):
    # coupon code by user
    coupon_code = request.GET.get('coupon_code')
    # get coupon object by coupon code
    coupon = Coupon.objects.filter(code=coupon_code).first()
    customer = request.user.customer
    bascet = customer.bascetitem_set.all()
    # get total price of bascet by multiplying price of each product by quantity
    bascet = bascet.annotate(total_price=F('product__price') * F('quantity'))
    # get total price of bascet by summing total price of each product
    total_bascet_price = bascet.aggregate(total_bascet_price=Sum('total_price')).get('total_bascet_price') or 0
    # get shipping price by multiplying total price of bascet by 7%
    shipping_price = total_bascet_price * 0.07
    # get total price by adding shipping price to total price of bascet
    total_price = total_bascet_price + shipping_price

    coupon_discount = None
    total_price_with_coupon = None
    # if coupon exists and is valid for customer then calculate total price with coupon and coupon discount
    if coupon:
        coupon_discount = total_price * coupon.discount_percent / 100
        total_price_with_coupon = total_price - coupon_discount
        
    context = {
        'bascet': bascet, 
        'total_bascet_price': total_bascet_price,
        'coupon_discount': coupon_discount,
        'shipping_price': shipping_price,
        'coupon': coupon,
        'total_price': total_price,
        'total_price_with_coupon': total_price_with_coupon,
        # check if there is a coupon code and if it is valid
        'coupon_found_and_is_valid': coupon and coupon.is_valid(customer),
        # check if there is a coupon code and it doesn't exist on database or it is not valid
        'coupone_code_exists_but_coupone_not_found_or_coupon_is_not_valid': bool(coupon_code and (not coupon or not coupon.is_valid(customer))),
        'coupon_code': coupon_code
    }
    
    return render(request, 'bascet.html', context=context)

@login_required
@csrf_protect
def update_bascet_quantity(request, pk):
    quantity = int(request.POST.get('quantity'))
    bascetitem = get_object_or_404(BascetItem, pk=pk)
    if quantity:
        bascetitem.quantity = quantity
        bascetitem.save()
    else:
        # if quantity is 0 then delete the bascet item
        bascetitem.delete()
    return redirect('customer:bascet')

@login_required
def remove_bascet(request, pk):
    get_object_or_404(BascetItem, pk=pk).delete()
    return redirect('customer:bascet')

@login_required
@csrf_protect
def checkout(request):
    user = request.user
    form = CheckoutForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})
    customer = request.user.customer
    coupon_code = request.GET.get('coupon_code')
    coupon = Coupon.objects.filter(code=coupon_code).first()
    bascet = customer.bascetitem_set.all()
    bascet = bascet.annotate(total_price=F('product__price') * F('quantity'))
    total_bascet_price = bascet.aggregate(total_bascet_price=Sum('total_price')).get('total_bascet_price')
    shipping_price = total_bascet_price * 0.07
    total_price = total_bascet_price + shipping_price

    coupon_discount = None
    total_price_with_coupon = None
    if coupon:
        coupon_discount = total_price * coupon.discount_percent / 100
        total_price_with_coupon = total_price - coupon_discount

    coupon_found_and_is_valid = coupon and coupon.is_valid(customer)
    coupone_code_exists_but_coupone_not_found_or_coupon_is_not_valid = bool(coupon_code and (not coupon or not coupon.is_valid(customer))),


    if request.method == 'POST':
        form = CheckoutForm(data=request.POST)
        if form.is_valid():
            order = form.save(
                customer, 
                total_price, 
                coupon, 
                coupon_found_and_is_valid, 
                total_price_with_coupon)
            return redirect('ecommerce:home')
        
    context = {
        'form': form,
        'bascet': bascet, 
        'total_bascet_price': total_bascet_price,
        'coupon_discount': coupon_discount,
        'shipping_price': shipping_price,
        'coupon': coupon,
        'total_price': total_price,
        'total_price_with_coupon': total_price_with_coupon,
        'coupon_found_and_is_valid': coupon_found_and_is_valid,
        'coupone_code_exists_but_coupone_not_found_or_coupon_is_not_valid': coupone_code_exists_but_coupone_not_found_or_coupon_is_not_valid,
        'coupon_code': coupon_code
    }
    
    return render(request, 'checkout.html', context)

# change currency and set currency ratio in session
currency_eq = {'USD': 0.59, 'TRY': 11.04, 'EUR': 0.56, 'AZN': 1}
def change_currency(request, currency):
    request.session['currency'] = currency
    request.session['currency_ratio'] = currency_eq.get(currency)
    return redirect(request.META.get('HTTP_REFERER'))


@csrf_protect
def reset_password(request, uuid, token):
    # find password reset object by uuid
    password_reset = get_object_or_404(PasswordReset, uuid=uuid)
    # check if token is valid
    if password_reset.is_valid(token):
        form = ResetPasswordForm()
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                form.change_password(password_reset)
                return redirect('customer:reset-password-notf', color='success', message='Şifre uğurla yenilendi!')
        return render(request, 'reset-password.html', {'form': form})
    
    return redirect('customer:reset-password-notf', color='danger', message='Linkiniz duzgun deyil!')
    

@csrf_protect
def reset_password_email(request):
    form = ResetPasswordEmailForm()
    if request.method == 'POST':
        form = ResetPasswordEmailForm(request.POST)
        if form.is_valid():
            # send reset password email if email is valid
            result = form.send_reset_mail(request)
            # if email is sent successfully then redirect to notification page
            if result:
                return redirect('customer:reset-password-notf', color='info', message='Ugurla gonderildi!')
            else:
                return redirect('customer:reset-password-notf', color='danger', message='Gonderilmede problem yasandi!')
    return render(request, 'reset-password-email.html', {'form': form})

# view for notification page after reset password
class ResetPasswordNotfView(TemplateView):
    template_name = 'reset-password-notf.html'
    
    def get_context_data(self, **kwargs):
        # show notification message and color from url
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        return context

# def reset_password_notf(request, color, message):
#     return render(request, 'reset-password-notf.html', {'color': color, 'message': message})