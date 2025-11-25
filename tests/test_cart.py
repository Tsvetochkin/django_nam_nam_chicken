import pytest
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
from cart.cart import Cart
from shop.models import Product


@pytest.mark.django_db
def test_add_to_cart(client, product):
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 2, 'update': False}
    )
    assert response.status_code == 302

    cart = Cart(client)
    assert len(cart) == 2


@pytest.mark.django_db
def test_update_quantity(client, product):
    cart = Cart(client)
    cart.add(product=product, quantity=2)
    cart.add(product=product, quantity=5, update_quantity=True)

    assert len(cart) == 5
    assert cart.cart[str(product.id)]['quantity'] == 5


@pytest.mark.django_db
def test_remove_from_cart(client, product):
    cart = Cart(client)
    cart.add(product=product, quantity=3)

    response = client.get(reverse('cart:cart_remove', args=[product.id]))

    cart = Cart(client)
    assert len(cart) == 0


@pytest.mark.django_db
def test_view_cart(client, product):
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 2, 'update': False}
    )

    response = client.get(reverse('cart:cart_detail'))
    assert response.status_code == 200
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_clear_cart(client, product):
    cart = Cart(client)
    cart.add(product=product, quantity=5)

    response = client.post(reverse('cart:cart_clear'))
    assert response.status_code == 302

    cart = Cart(client)
    assert len(cart) == 0


@pytest.mark.django_db
def test_cart_session_persistence(client, product):
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 3, 'update': False}
    )

    assert settings.CART_SESSION_ID in client.session
    assert str(product.id) in client.session[settings.CART_SESSION_ID]


@pytest.mark.django_db
def test_cart_total_calculation(client, product, category):
    another_product = Product.objects.create(
        category=category,
        name='Another Product',
        slug='another-product',
        price=Decimal('15.00'),
        stock=10,
        available=True
    )

    cart = Cart(client)
    cart.add(product=product, quantity=2)
    cart.add(product=another_product, quantity=1)

    expected_total = (product.price * 2) + (another_product.price * 1)
    assert cart.get_total_price() == expected_total


@pytest.mark.django_db
def test_coupon_application(client, product, valid_coupon):
    cart = Cart(client)
    cart.add(product=product, quantity=1)

    response = client.post(reverse('cart:apply_coupon'), {'coupon_code': valid_coupon.code})
    assert response.status_code == 302

    cart = Cart(client)
    assert cart.coupon is not None
    assert cart.coupon.code == valid_coupon.code


@pytest.mark.django_db
def test_coupon_discount(client, product, valid_coupon):
    cart = Cart(client)
    cart.add(product=product, quantity=1)
    cart.apply_coupon(valid_coupon)

    discount = cart.get_discount()
    expected_discount = product.price * Decimal('0.20')
    assert discount == expected_discount

    total_after_discount = cart.get_total_price_after_discount()
    assert total_after_discount == product.price - discount


@pytest.mark.django_db
def test_invalid_coupon(client, product):
    cart = Cart(client)
    cart.add(product=product, quantity=1)

    response = client.post(reverse('cart:apply_coupon'), {'coupon_code': 'INVALID'})
    assert response.status_code == 302

    cart = Cart(client)
    assert cart.coupon is None


@pytest.mark.django_db
def test_expired_coupon(client, product, expired_coupon):
    cart = Cart(client)
    cart.add(product=product, quantity=1)

    response = client.post(reverse('cart:apply_coupon'), {'coupon_code': expired_coupon.code})

    cart = Cart(client)
    assert not expired_coupon.is_valid()


@pytest.mark.django_db
def test_remove_coupon(client, product, valid_coupon):
    cart = Cart(client)
    cart.add(product=product, quantity=1)
    cart.apply_coupon(valid_coupon)

    response = client.post(reverse('cart:remove_coupon'))
    assert response.status_code == 302

    cart = Cart(client)
    assert cart.coupon is None
