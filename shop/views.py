from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import mercadopago
import json
import hmac
import hashlib

from .models import Category, Product, Order, OrderItem, Review
from .forms import OrderCreateForm, ReviewForm
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
    
    if request.method == 'POST' and request.user.is_authenticated:
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
        if request.user.is_authenticated:
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                review_form = ReviewForm(instance=existing_review)
            else:
                review_form = ReviewForm()
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
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            for item in cart:
                product = item['product']
                quantity = item['quantity']

                OrderItem.objects.create(order=order,
                                         product=product,
                                         price=item['price'],
                                         quantity=quantity)

            # Create MercadoPago preference
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            items = []
            for item in order.items.all():
                items.append({
                    "title": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.price),
                })

            base_url = "https://dev.yokotoka.is"
            preference_data = {
                "items": items,
                "back_urls": {
                    "success": f"{base_url}/payment-success/{order.id}/",
                    "failure": f"{base_url}/payment-failure/{order.id}/",
                    "pending": f"{base_url}/payment-pending/{order.id}/"
                },
                "auto_return": "approved",
                "notification_url": f"{base_url}/webhook/",
                "external_reference": str(order.id),
            }

            preference_response = sdk.preference().create(preference_data)

            # Log the response for debugging
            print(f"MercadoPago Response: {preference_response}")
            print(f"Response status: {preference_response.get('status')}")
            print(f"Response body: {preference_response.get('response')}")

            if preference_response.get('status') == 201:
                preference = preference_response.get("response", {})
                preference_id = preference.get('id')
                sandbox_init_point = preference.get('sandbox_init_point')
            else:
                print(f"MercadoPago API Error: {preference_response}")
                preference_id = None
                sandbox_init_point = None

            return render(request, 'shop/order/payment.html', {
                'order': order,
                'preference_id': preference_id,
                'sandbox_init_point': sandbox_init_point,
                'public_key': settings.MERCADOPAGO_PUBLIC_KEY
            })
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


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.paid = True
    order.status = Order.STATUS_PAID
    order.save()

    # Reduce stock
    for item in order.items.all():
        product = item.product
        if product.stock >= item.quantity:
            product.stock -= item.quantity
            product.save()

    # Clear cart
    cart = Cart(request)
    cart.clear()

    # Send email
    subject = f'Order nr. {order.id} from Nam Nam Chicken'
    html_message = render_to_string('shop/order/order_confirmation_email.html', {'order': order})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [order.email], html_message=html_message)

    messages.success(request, f'Payment successful! Order {order.id} confirmed.')
    return render(request, 'shop/order/created.html', {'order': order})


def payment_failure(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    messages.error(request, 'Payment failed. Please try again.')
    return render(request, 'shop/payment/failure.html', {'order': order})


def payment_pending(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    messages.info(request, 'Payment is pending. We will notify you when it is confirmed.')
    return render(request, 'shop/payment/pending.html', {'order': order})


@csrf_exempt
def mercadopago_webhook(request):
    if request.method == 'POST':
        try:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            # Check query params first (IPN style)
            topic = request.GET.get('topic')
            resource_id = request.GET.get('id')

            if topic == 'merchant_order' and resource_id:
                # Get merchant order details
                merchant_order = sdk.merchant_order().get(resource_id)
                if merchant_order['status'] == 200:
                    order_data = merchant_order['response']
                    external_reference = order_data.get('external_reference')

                    # Check if all payments are approved
                    payments = order_data.get('payments', [])
                    paid_amount = sum(p['transaction_amount'] for p in payments if p['status'] == 'approved')

                    if paid_amount >= order_data.get('total_amount', 0) and external_reference:
                        try:
                            order = Order.objects.get(id=external_reference)
                            if not order.paid:
                                order.paid = True
                                order.status = Order.STATUS_PAID
                                order.save()
                                for item in order.items.all():
                                    product = item.product
                                    product.stock -= item.quantity
                                    product.save()
                        except Order.DoesNotExist:
                            pass
                return HttpResponse(status=200)

            # Check body for webhook v2 style
            data = json.loads(request.body.decode('utf-8')) if request.body else {}

            if data.get('type') == 'payment':
                payment_id = data.get('data', {}).get('id')
                payment_info = sdk.payment().get(payment_id)

                if payment_info['status'] == 200:
                    payment = payment_info['response']
                    external_reference = payment.get('external_reference')

                    if external_reference:
                        try:
                            order = Order.objects.get(id=external_reference)
                            if payment['status'] == 'approved' and not order.paid:
                                order.paid = True
                                order.status = Order.STATUS_PAID
                                order.save()
                                for item in order.items.all():
                                    product = item.product
                                    product.stock -= item.quantity
                                    product.save()
                        except Order.DoesNotExist:
                            pass

            return HttpResponse(status=200)
        except Exception as e:
            print(f"Webhook error: {e}")
            return HttpResponse(status=200)  # Always return 200 to avoid retries

    return HttpResponse(status=405)


@csrf_exempt
def mercadopago_ipn(request):
    if request.method in ('POST', 'GET'):
        topic = request.GET.get('topic') or request.POST.get('topic')
        resource_id = request.GET.get('id') or request.POST.get('id')

        if not topic or not resource_id:
            return HttpResponse(status=200)

        try:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            if topic == 'payment':
                payment_info = sdk.payment().get(resource_id)
                if payment_info.get('status') == 200:
                    payment = payment_info['response']
                    external_reference = payment.get('external_reference')
                    if external_reference and payment.get('status') == 'approved':
                        try:
                            order = Order.objects.get(id=external_reference)
                            if not order.paid:
                                order.paid = True
                                order.status = Order.STATUS_PAID
                                order.save()
                                for item in order.items.all():
                                    product = item.product
                                    product.stock -= item.quantity
                                    product.save()
                        except Order.DoesNotExist:
                            pass

            elif topic == 'merchant_order':
                merchant_order = sdk.merchant_order().get(resource_id)
                if merchant_order.get('status') == 200:
                    order_data = merchant_order['response']
                    external_reference = order_data.get('external_reference')
                    payments = order_data.get('payments', [])
                    paid_amount = sum(p['transaction_amount'] for p in payments if p['status'] == 'approved')
                    if paid_amount >= order_data.get('total_amount', 0) and external_reference:
                        try:
                            order = Order.objects.get(id=external_reference)
                            if not order.paid:
                                order.paid = True
                                order.status = Order.STATUS_PAID
                                order.save()
                                for item in order.items.all():
                                    product = item.product
                                    product.stock -= item.quantity
                                    product.save()
                        except Order.DoesNotExist:
                            pass

        except Exception as e:
            print(f"IPN error: {e}")

        return HttpResponse(status=200)

    return HttpResponse(status=200)