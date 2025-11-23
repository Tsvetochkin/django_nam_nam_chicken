from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages

from .models import Category, Product, Order, OrderItem, Review # Import Review model
from .forms import OrderCreateForm, ReviewForm # Import ReviewForm
from cart.cart import Cart
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    query = request.GET.get('q')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request,
                  'shop/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})


def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    
    reviews = product.reviews.all()
    
    if request.method == 'POST':
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        
        if existing_review:
            review_form = ReviewForm(request.POST, instance=existing_review)
        else:
            review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Tu reseña ha sido enviada con éxito.')
            return redirect(product.get_absolute_url())
        else:
            messages.error(request, 'Hubo un error al enviar tu reseña. Por favor, verifica los datos.')
    else:
        # If user already reviewed, pre-fill the form with their review
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        if existing_review:
            review_form = ReviewForm(instance=existing_review)
        else:
            review_form = ReviewForm()

    return render(request,
                  'shop/product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form,
                   'reviews': reviews,
                   'review_form': review_form})


def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('shop:product_list') # Redirect if cart is empty

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.paid = True # Simulate payment
            order.save()

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            messages.success(request, f'Order {order.id} has been successfully placed!') # Add success message

            # Simulate sending email
            subject = f'Order nr. {order.id} from Nam Nam Chicken'
            html_message = render_to_string('shop/order/order_confirmation_email.html', {'order': order})
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = order.email

            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

            return render(request,
                          'shop/order/created.html',
                          {'order': order})
    else:
        # Pre-fill form for authenticated users
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'address': getattr(request.user.profile, 'address', ''),
                'celular': getattr(request.user.profile, 'celular', ''), # New field
            }
            form = OrderCreateForm(initial=initial_data)
        else:
            form = OrderCreateForm()
    return render(request,
                  'shop/order/create.html',
                  {'cart': cart, 'form': form})