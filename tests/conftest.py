import pytest
from decimal import Decimal
from unittest.mock import Mock, patch


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def another_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )


@pytest.fixture
def category(db):
    from shop.models import Category
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )


@pytest.fixture
def product(db, category):
    from shop.models import Product
    return Product.objects.create(
        category=category,
        name='Test Product',
        slug='test-product',
        description='Test product description',
        price=Decimal('19.99'),
        stock=10,
        available=True
    )


@pytest.fixture
def product_out_of_stock(db, category):
    from shop.models import Product
    return Product.objects.create(
        category=category,
        name='Out of Stock Product',
        slug='out-of-stock',
        description='No stock',
        price=Decimal('29.99'),
        stock=0,
        available=True
    )


@pytest.fixture
def unavailable_product(db, category):
    from shop.models import Product
    return Product.objects.create(
        category=category,
        name='Unavailable Product',
        slug='unavailable',
        description='Not available',
        price=Decimal('39.99'),
        stock=5,
        available=False
    )


@pytest.fixture
def order(db, user, product):
    from shop.models import Order, OrderItem
    order_obj = Order.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        email='john@example.com',
        address='123 Test Street',
        celular='1234567890'
    )
    OrderItem.objects.create(
        order=order_obj,
        product=product,
        price=product.price,
        quantity=2
    )
    return order_obj


@pytest.fixture
def valid_coupon(db):
    from django.utils import timezone
    from datetime import timedelta
    from shop.models import Coupon
    now = timezone.now()
    return Coupon.objects.create(
        code='TESTCODE',
        discount_percent=20,
        valid_from=now - timedelta(days=1),
        valid_to=now + timedelta(days=30),
        active=True,
        usage_limit=10,
        used_count=0
    )


@pytest.fixture
def expired_coupon(db):
    from django.utils import timezone
    from datetime import timedelta
    from shop.models import Coupon
    now = timezone.now()
    return Coupon.objects.create(
        code='EXPIRED',
        discount_percent=15,
        valid_from=now - timedelta(days=30),
        valid_to=now - timedelta(days=1),
        active=True,
        usage_limit=10,
        used_count=0
    )


@pytest.fixture
def cart(client):
    from cart.cart import Cart
    return Cart(client)


@pytest.fixture
def review(db, user, product):
    from shop.models import Review
    return Review.objects.create(
        product=product,
        user=user,
        rating=4,
        comment='Great product!'
    )


@pytest.fixture
def wishlist_item(db, user, product):
    from users.models import WishlistItem
    return WishlistItem.objects.create(
        user=user,
        product=product
    )


@pytest.fixture(autouse=True)
def mock_mercadopago():
    with patch('shop.views.mercadopago') as mock_mp:
        mock_sdk = Mock()
        mock_preference = Mock()
        mock_preference.create.return_value = {
            'response': {
                'id': 'test_preference_id_123',
                'init_point': 'https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=test_preference_id_123'
            }
        }
        mock_sdk.preference.return_value = mock_preference
        mock_mp.SDK.return_value = mock_sdk
        yield mock_mp
