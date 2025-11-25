from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from shop.models import Product, Coupon
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
        if cd['update']:
            messages.success(request, f'Quantity for {product.name} updated in your cart.')
        else:
            messages.success(request, f'{product.name} added to your cart.')
    return redirect('cart:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from your cart.')
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'],
                                                                   'update': True})
    return render(request, 'cart/detail.html', {'cart': cart})

@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Your shopping cart has been cleared.')
    return redirect('cart:cart_detail')

@require_POST
def apply_coupon(request):
    cart = Cart(request)
    coupon_code = request.POST.get('coupon_code', '').strip().upper()

    if not coupon_code:
        messages.error(request, 'Please enter a coupon code.')
        return redirect('cart:cart_detail')

    try:
        coupon = Coupon.objects.get(code__iexact=coupon_code)
        if coupon.is_valid():
            cart.apply_coupon(coupon)
            coupon.used_count += 1
            coupon.save()
            messages.success(request, f'Coupon "{coupon.code}" applied! You get {coupon.discount_percent}% off.')
        else:
            messages.error(request, 'This coupon is no longer valid.')
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid coupon code.')

    return redirect('cart:cart_detail')

@require_POST
def remove_coupon(request):
    cart = Cart(request)
    cart.clear_coupon()
    messages.success(request, 'Coupon removed from cart.')
    return redirect('cart:cart_detail')