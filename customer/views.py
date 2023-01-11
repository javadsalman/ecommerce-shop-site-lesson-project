from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    RegisterForm, ContactForm, CheckoutForm
)
from django.contrib.auth import login, logout, authenticate
from ecommerce.models import Product
from .models import (
    Customer, Wish, BascetItem, Order, Coupon
)
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
import requests
import os

RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

# Create your views here.

def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        response = requests.post(' https://www.google.com/recaptcha/api/siteverify', {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': request.POST.get('g-recaptcha-response')
        })
        recaptcha_result = response.json()
        success = recaptcha_result.get('success')
        score = recaptcha_result.get('score')
        if form.is_valid() and success and score > 0.7:
            form.save()
            return render(request, 'contact.html', context={'form': ContactForm(), 'status': 'success'})
        return render(request, 'contact.html', context={'form': form, 'status': 'fail'})
    return render(request, 'contact.html', context={'form': form})



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
            return redirect(nextUrl or 'ecommerce:home')
        return render(request, 'login.html', context={'unsuccess': True})

def logout_view(request):
    logout(request)
    return redirect('customer:login')

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', context={'form': form})
        
    elif request.method == 'POST':
        form = RegisterForm(data=request.POST)
        accepted = request.POST.get('accepted')
        if form.is_valid() and accepted:
            customer = form.save()
            login(request, customer.user)
            return redirect('ecommerce:home')
        elif not accepted:
            return render(request, 'register.html', context={'form': form, 'not_accepted':True})
        else:
            return render(request, 'register.html', context={'form': form})


@login_required
def wishlist(request):
    customer = request.user.customer
    wishlist = customer.wish_set.all()
    return render(request, 'wishlist.html', context={'wishlist': wishlist})



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
def bascet(request):
    coupon_code = request.GET.get('coupon_code')
    coupon = Coupon.objects.filter(code=coupon_code).first()
    customer = request.user.customer
    bascet = customer.bascetitem_set.all()
    bascet = bascet.annotate(total_price=F('product__price') * F('quantity'))
    total_bascet_price = bascet.aggregate(total_bascet_price=Sum('total_price')).get('total_bascet_price') or 0
    shipping_price = total_bascet_price * 0.07
    total_price = total_bascet_price + shipping_price

    coupon_discount = None
    total_price_with_coupon = None
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
        'coupon_found_and_is_valid': coupon and coupon.is_valid(customer),
        'coupone_code_exists_but_coupone_not_found_or_coupon_is_not_valid': bool(coupon_code and (not coupon or not coupon.is_valid(customer))),
        'coupon_code': coupon_code
    }
    
    return render(request, 'bascet.html', context=context)

@login_required
def update_bascet_quantity(request, pk):
    quantity = int(request.POST.get('quantity'))
    bascetitem = get_object_or_404(BascetItem, pk=pk)
    if quantity:
        bascetitem.quantity = quantity
        bascetitem.save()
    else:
        bascetitem.delete()
    return redirect('customer:bascet')

@login_required
def remove_bascet(request, pk):
    get_object_or_404(BascetItem, pk=pk).delete()
    return redirect('customer:bascet')

@login_required
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


currency_eq = {'USD': 0.59, 'TRY': 11.04, 'EUR': 0.56, 'AZN': 1}
def change_currency(request, currency):
    request.session['currency'] = currency
    request.session['currency_ratio'] = currency_eq.get(currency)
    return redirect(request.META.get('HTTP_REFERER'))