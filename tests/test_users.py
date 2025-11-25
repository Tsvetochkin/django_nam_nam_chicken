import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import Profile, WishlistItem
from shop.models import Order

User = get_user_model()


@pytest.mark.django_db
def test_user_registration(client):
    response = client.post(reverse('users:register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'ComplexPass123!',
        'password2': 'ComplexPass123!'
    })
    assert response.status_code == 302
    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_user_registration_invalid(client):
    response = client.post(reverse('users:register'), {
        'username': 'newuser',
        'email': 'invalid-email',
        'password1': 'pass',
        'password2': 'different'
    })
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_user_login(client, user):
    response = client.post(reverse('users:login'), {
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_logout(client, user):
    client.login(username='testuser', password='testpass123')
    response = client.post(reverse('users:logout'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_profile_auto_creation(user):
    assert hasattr(user, 'profile')
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_profile_view(client, user):
    client.force_login(user)
    response = client.get(reverse('users:profile'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_view_requires_auth(client):
    response = client.get(reverse('users:profile'))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_purchase_history(client, user, order):
    client.force_login(user)
    response = client.get(reverse('users:purchase_history'))
    assert response.status_code == 200
    assert str(order.id) in response.content.decode()


@pytest.mark.django_db
def test_wishlist_add(client, user, product):
    client.force_login(user)
    response = client.post(reverse('users:wishlist_add', args=[product.id]))
    assert response.status_code == 302
    assert WishlistItem.objects.filter(user=user, product=product).exists()


@pytest.mark.django_db
def test_wishlist_remove(client, user, wishlist_item):
    client.force_login(user)
    response = client.get(reverse('users:wishlist_remove', args=[wishlist_item.id]))
    assert response.status_code == 302
    assert not WishlistItem.objects.filter(id=wishlist_item.id).exists()


@pytest.mark.django_db
def test_wishlist_duplicate_prevention(client, user, product):
    client.force_login(user)

    client.post(reverse('users:wishlist_add', args=[product.id]))
    client.post(reverse('users:wishlist_add', args=[product.id]))

    assert WishlistItem.objects.filter(user=user, product=product).count() == 1


@pytest.mark.django_db
def test_wishlist_view(client, user, wishlist_item):
    client.force_login(user)
    response = client.get(reverse('users:wishlist'))
    assert response.status_code == 200
    assert wishlist_item.product.name in response.content.decode()


@pytest.mark.django_db
def test_profile_string_representation(user):
    assert str(user.profile) == f'Profile for user {user.username}'


@pytest.mark.django_db
def test_wishlist_requires_auth(client, product):
    response = client.post(reverse('users:wishlist_add', args=[product.id]))
    assert response.status_code == 302
    assert '/login/' in response.url
