from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Import messages
from .forms import UserRegistrationForm
from shop.models import Order

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request, 'Registration successful. You are now logged in.') # Add success message
            return redirect('shop:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)
    return render(request,
                  'users/profile.html',
                  {'orders': orders})

@login_required
def purchase_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'users/purchase_history.html', {'orders': orders})