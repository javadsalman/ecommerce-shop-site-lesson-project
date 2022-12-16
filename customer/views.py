from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    RegisterForm, ContactForm
)
from django.contrib.auth import login, logout, authenticate
from ecommerce.models import Product
from .models import (
    Customer, Wish, BascetItem, Order
)
from django.contrib.auth.decorators import login_required
from django.db.models import F

# Create your views here.

def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('ecommerce:home')
    return render(request, 'contact.html', context={'form': form})




@login_required
def checkout(request):
    return render(request, 'checkout.html')

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print('USER', user)
        if user:
            login(request, user)
            nextUrl = request.GET.get('next')
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
    bascet = request.user.customer.bascetitem_set.all()
    bascet = bascet.annotate(total_price=F('product__price') * F('quantity'))
    return render(request, 'bascet.html', context={'bascet': bascet})

@login_required
def update_bascet_quantity(request, pk):
    quantity = request.POST.get('quantity')
    bascet = get_object_or_404(BascetItem, pk=pk)
    bascet.quantity = quantity
    bascet.save()
    return redirect('customer:bascet')