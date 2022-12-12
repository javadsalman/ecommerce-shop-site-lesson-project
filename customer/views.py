from django.shortcuts import render, redirect
from .forms import (
    RegisterForm
)
from django.contrib.auth import login, logout, authenticate

# Create your views here.

def contact(request):
    return render(request, 'contact.html')

def wishlist(request):
    return render(request, 'wishlist.html')

def bascet(request):
    return render(request, 'bascet.html')

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
            return redirect('ecommerce:home')
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