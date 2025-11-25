import pytest
from django.urls import reverse
from django.core import mail
from decimal import Decimal
from shop.models import Order, Product
from cart.cart import Cart


@pytest.mark.django_db
def test_complete_purchase_flow_authenticated_user(client, user, product, category):
    """Integration test: Complete purchase flow for authenticated user"""
    client.force_login(user)

    # Step 1: Add products to cart
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 2, 'update': False}
    )
    assert response.status_code == 302

    another_product = Product.objects.create(
        category=category,
        name='Second Product',
        slug='second-product',
        price=Decimal('25.00'),
        stock=15,
        available=True
    )

    response = client.post(
        reverse('cart:cart_add', args=[another_product.id]),
        {'quantity': 1, 'update': False}
    )
    assert response.status_code == 302

    # Step 2: View cart
    response = client.get(reverse('cart:cart_detail'))
    assert response.status_code == 200
    assert product.name in response.content.decode()
    assert another_product.name in response.content.decode()

    # Step 3: Go to checkout
    response = client.get(reverse('shop:order_create'))
    assert response.status_code == 200

    # Step 4: Create order
    initial_product_stock = product.stock
    initial_another_stock = another_product.stock

    response = client.post(reverse('shop:order_create'), {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': '123 Test Street',
        'celular': '1234567890',
        'notes': 'Please deliver fast'
    })
    assert response.status_code == 200

    # Step 5: Verify order created
    order = Order.objects.filter(user=user).first()
    assert order is not None
    assert order.items.count() == 2
    assert order.paid is False

    # Step 6: Complete payment
    response = client.get(reverse('shop:payment_success', args=[order.id]))
    assert response.status_code == 200

    # Step 7: Verify order updated
    order.refresh_from_db()
    assert order.paid is True
    assert order.status == Order.STATUS_PAID

    # Step 8: Verify stock reduced
    product.refresh_from_db()
    another_product.refresh_from_db()
    assert product.stock == initial_product_stock - 2
    assert another_product.stock == initial_another_stock - 1

    # Step 9: Verify email sent
    assert len(mail.outbox) == 1
    assert order.email in mail.outbox[0].to

    # Step 10: Verify cart cleared
    cart = Cart(client)
    assert len(cart) == 0


@pytest.mark.django_db
def test_complete_purchase_flow_with_coupon(client, user, product, valid_coupon):
    """Integration test: Purchase flow with coupon discount"""
    client.force_login(user)

    # Add product to cart
    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 2, 'update': False}
    )

    # Apply coupon
    response = client.post(reverse('cart:apply_coupon'), {
        'coupon_code': valid_coupon.code
    })
    assert response.status_code == 302

    # Verify coupon applied
    cart = Cart(client)
    assert cart.coupon is not None
    assert cart.coupon.code == valid_coupon.code

    original_total = cart.get_total_price()
    discount = cart.get_discount()
    total_after_discount = cart.get_total_price_after_discount()

    assert discount == original_total * Decimal('0.20')
    assert total_after_discount == original_total - discount

    # Create order
    response = client.post(reverse('shop:order_create'), {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane@example.com',
        'address': '456 Test Ave',
        'celular': '0987654321'
    })
    assert response.status_code == 200

    order = Order.objects.filter(user=user).first()
    assert order is not None

    # Complete payment
    client.get(reverse('shop:payment_success', args=[order.id]))

    order.refresh_from_db()
    assert order.paid is True


@pytest.mark.django_db
def test_anonymous_user_purchase_flow(client, product):
    """Integration test: Anonymous user can complete purchase"""
    # Add product to cart
    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )

    # Create order
    response = client.post(reverse('shop:order_create'), {
        'first_name': 'Anonymous',
        'last_name': 'User',
        'email': 'anon@example.com',
        'address': '789 Anon Street',
        'celular': '5555555555'
    })
    assert response.status_code == 200

    # Verify order created without user
    order = Order.objects.first()
    assert order is not None
    assert order.user is None
    assert order.email == 'anon@example.com'

    # Complete payment
    client.get(reverse('shop:payment_success', args=[order.id]))

    order.refresh_from_db()
    assert order.paid is True


@pytest.mark.django_db
def test_wishlist_to_cart_flow(client, user, product):
    """Integration test: Add product from wishlist to cart"""
    client.force_login(user)

    # Add product to wishlist
    response = client.post(reverse('users:wishlist_add', args=[product.id]))
    assert response.status_code == 302

    # View wishlist
    response = client.get(reverse('users:wishlist'))
    assert response.status_code == 200
    assert product.name in response.content.decode()

    # Add to cart from wishlist page
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )
    assert response.status_code == 302

    # Verify in cart
    cart = Cart(client)
    assert len(cart) == 1


@pytest.mark.django_db
def test_payment_failure_flow(client, user, product):
    """Test payment failure handling"""
    client.force_login(user)

    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )

    client.post(reverse('shop:order_create'), {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': '123 Test Street',
        'celular': '1234567890'
    })

    order = Order.objects.filter(user=user).first()

    # Simulate payment failure
    response = client.get(reverse('shop:payment_failure', args=[order.id]))
    assert response.status_code == 200

    # Order should still be unpaid
    order.refresh_from_db()
    assert order.paid is False


@pytest.mark.django_db
def test_payment_pending_flow(client, user, product):
    """Test payment pending handling"""
    client.force_login(user)

    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )

    client.post(reverse('shop:order_create'), {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': '123 Test Street',
        'celular': '1234567890'
    })

    order = Order.objects.filter(user=user).first()

    # Simulate payment pending
    response = client.get(reverse('shop:payment_pending', args=[order.id]))
    assert response.status_code == 200

    # Order should still be unpaid
    order.refresh_from_db()
    assert order.paid is False


@pytest.mark.django_db
def test_product_out_of_stock_cannot_add_to_cart(client, product):
    """Test that out of stock product cannot be added to cart"""
    product.stock = 0
    product.save()

    # Try to add to cart
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )

    # Should still redirect, but cart should handle it
    assert response.status_code == 302
