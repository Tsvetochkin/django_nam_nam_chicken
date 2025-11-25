import pytest
from django.urls import reverse
from django.core import mail
from decimal import Decimal
from shop.models import Order, OrderItem, Product
from cart.cart import Cart


@pytest.mark.django_db
def test_create_order(client, user, product):
    client.force_login(user)
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 2, 'update': False}
    )

    response = client.post(reverse('shop:order_create'), {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': '123 Test Street',
        'celular': '1234567890',
        'notes': 'Please deliver fast'
    })
    assert response.status_code == 200
    assert Order.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_order_requires_cart(client, user):
    client.force_login(user)
    response = client.get(reverse('shop:order_create'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_order_reduces_stock(client, user, product):
    client.force_login(user)
    initial_stock = product.stock

    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 3, 'update': False}
    )

    client.post(reverse('shop:order_create'), {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': '123 Test Street',
        'celular': '1234567890'
    })

    order = Order.objects.first()
    response = client.get(reverse('shop:payment_success', args=[order.id]))
    assert response.status_code == 200

    product.refresh_from_db()
    assert product.stock == initial_stock - 3


@pytest.mark.django_db
def test_order_items_created(client, user, product, category):
    client.force_login(user)

    another_product = Product.objects.create(
        category=category,
        name='Another Product',
        slug='another-product',
        price=Decimal('25.00'),
        stock=10,
        available=True
    )

    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 2, 'update': False}
    )
    client.post(
        reverse('cart:cart_add', args=[another_product.id]),
        {'quantity': 1, 'update': False}
    )

    client.post(reverse('shop:order_create'), {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane@example.com',
        'address': '456 Test Ave',
        'celular': '0987654321'
    })

    order = Order.objects.first()
    assert order.items.count() == 2
    assert OrderItem.objects.filter(order=order, product=product).exists()
    assert OrderItem.objects.filter(order=order, product=another_product).exists()


@pytest.mark.django_db
def test_order_total_cost(order, product):
    expected_total = product.price * 2
    assert order.get_total_cost() == expected_total


@pytest.mark.django_db
def test_order_status_field(order):
    assert order.status == Order.STATUS_PENDING

    order.status = Order.STATUS_PAID
    order.save()
    assert order.status == Order.STATUS_PAID


@pytest.mark.django_db
def test_order_paid_status(client, user, product):
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

    order = Order.objects.first()
    assert order.paid is False

    client.get(reverse('shop:payment_success', args=[order.id]))
    order.refresh_from_db()

    assert order.paid is True
    assert order.status == Order.STATUS_PAID


@pytest.mark.django_db
def test_order_confirmation_email(client, user, product):
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

    order = Order.objects.first()
    client.get(reverse('shop:payment_success', args=[order.id]))

    assert len(mail.outbox) == 1
    assert order.email in mail.outbox[0].to


@pytest.mark.django_db
def test_order_string_representation(order):
    assert str(order) == f'Order {order.id}'


@pytest.mark.django_db
def test_order_item_cost_calculation(order, product):
    order_item = order.items.first()
    expected_cost = product.price * order_item.quantity
    assert order_item.get_cost() == expected_cost


@pytest.mark.django_db
def test_anonymous_order_creation(client, product):
    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )

    response = client.post(reverse('shop:order_create'), {
        'first_name': 'Anonymous',
        'last_name': 'User',
        'email': 'anon@example.com',
        'address': '789 Anon Street',
        'celular': '5555555555'
    })

    assert response.status_code == 200
    order = Order.objects.first()
    assert order.user is None
    assert order.email == 'anon@example.com'


@pytest.mark.django_db
def test_cart_cleared_after_payment(client, user, product):
    client.force_login(user)
    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 2, 'update': False}
    )

    client.post(reverse('shop:order_create'), {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': '123 Test Street',
        'celular': '1234567890'
    })

    order = Order.objects.first()
    client.get(reverse('shop:payment_success', args=[order.id]))

    cart = Cart(client)
    assert len(cart) == 0
