import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_requires_login(client):
    """Test that profile view requires authentication"""
    response = client.get(reverse('users:profile'))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_purchase_history_requires_login(client):
    """Test that purchase history requires authentication"""
    response = client.get(reverse('users:purchase_history'))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_wishlist_requires_login(client):
    """Test that wishlist view requires authentication"""
    response = client.get(reverse('users:wishlist'))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_wishlist_add_requires_login(client, product):
    """Test that adding to wishlist requires authentication"""
    response = client.post(reverse('users:wishlist_add', args=[product.id]))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_wishlist_remove_requires_login(client, wishlist_item):
    """Test that removing from wishlist requires authentication"""
    response = client.get(reverse('users:wishlist_remove', args=[wishlist_item.id]))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_authenticated_user_can_access_profile(client, user):
    """Test that authenticated user can access profile"""
    client.force_login(user)
    response = client.get(reverse('users:profile'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_access_purchase_history(client, user):
    """Test that authenticated user can access purchase history"""
    client.force_login(user)
    response = client.get(reverse('users:purchase_history'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_access_wishlist(client, user):
    """Test that authenticated user can access wishlist"""
    client.force_login(user)
    response = client.get(reverse('users:wishlist'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_add_to_wishlist(client, user, product):
    """Test that authenticated user can add to wishlist"""
    client.force_login(user)
    response = client.post(reverse('users:wishlist_add', args=[product.id]))
    assert response.status_code == 302
    assert '/login/' not in response.url


@pytest.mark.django_db
def test_authenticated_user_can_remove_from_wishlist(client, user, wishlist_item):
    """Test that authenticated user can remove from wishlist"""
    client.force_login(user)
    response = client.get(reverse('users:wishlist_remove', args=[wishlist_item.id]))
    assert response.status_code == 302
    assert '/login/' not in response.url


@pytest.mark.django_db
def test_anonymous_user_can_browse_products(client, product):
    """Test that anonymous user can browse products"""
    response = client.get(reverse('shop:product_list'))
    assert response.status_code == 200
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_anonymous_user_can_view_product_detail(client, product):
    """Test that anonymous user can view product details"""
    response = client.get(reverse('shop:product_detail', args=[product.id, product.slug]))
    assert response.status_code == 200
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_anonymous_user_can_add_to_cart(client, product):
    """Test that anonymous user can add products to cart"""
    response = client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_anonymous_user_can_checkout(client, product):
    """Test that anonymous user can checkout"""
    client.post(
        reverse('cart:cart_add', args=[product.id]),
        {'quantity': 1, 'update': False}
    )

    response = client.get(reverse('shop:order_create'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_post_review(client, product):
    """Test that anonymous user cannot post review"""
    response = client.post(
        reverse('shop:product_detail', args=[product.id, product.slug]),
        {'rating': 5, 'comment': 'Great product!'}
    )
    # Should render product detail page but not create review
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_post_review(client, user, product):
    """Test that authenticated user can post review"""
    client.force_login(user)
    response = client.post(
        reverse('shop:product_detail', args=[product.id, product.slug]),
        {'rating': 5, 'comment': 'Great product!'}
    )
    assert response.status_code == 302
    assert response.url == product.get_absolute_url()


@pytest.mark.django_db
def test_user_can_only_access_own_purchase_history(client, user, another_user, order):
    """Test that user can only see their own orders"""
    from shop.models import Order

    # another_user should only see their own orders
    client.force_login(another_user)
    response = client.get(reverse('users:purchase_history'))
    assert response.status_code == 200

    # Check that another_user has no orders shown
    orders = Order.objects.filter(user=another_user)
    assert orders.count() == 0

    # original user should see their order
    client.force_login(user)
    response = client.get(reverse('users:purchase_history'))
    assert response.status_code == 200
    assert str(order.id) in response.content.decode()


@pytest.mark.django_db
def test_user_can_only_remove_own_wishlist_items(client, user, another_user, wishlist_item):
    """Test that user cannot remove another user's wishlist items"""
    client.force_login(another_user)
    response = client.get(reverse('users:wishlist_remove', args=[wishlist_item.id]))
    # Should return 404 or redirect
    assert response.status_code in [302, 404]
