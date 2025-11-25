from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm
from .models import WishlistItem
from shop.models import Order, Product

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

@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'users/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
@require_POST
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    if created:
        messages.success(request, f'{product.name} added to your wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

@login_required
def wishlist_remove(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'{product_name} removed from your wishlist.')
    return redirect('users:wishlist')