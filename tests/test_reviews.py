import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError
from shop.models import Review


@pytest.mark.django_db
def test_create_review(client, user, product):
    client.force_login(user)
    response = client.post(
        reverse('shop:product_detail', args=[product.id, product.slug]),
        {'rating': 5, 'comment': 'Excellent product!'}
    )
    assert response.status_code == 302
    assert Review.objects.filter(product=product, user=user).exists()


@pytest.mark.django_db
def test_review_rating_validation(user, product):
    review = Review(product=product, user=user, rating=5, comment='Great!')
    review.full_clean()

    review_invalid_low = Review(product=product, user=user, rating=0, comment='Bad')
    with pytest.raises(ValidationError):
        review_invalid_low.full_clean()

    review_invalid_high = Review(product=product, user=user, rating=6, comment='Too high')
    with pytest.raises(ValidationError):
        review_invalid_high.full_clean()


@pytest.mark.django_db
def test_one_review_per_user(user, product):
    Review.objects.create(product=product, user=user, rating=4, comment='Good')

    from django.db import IntegrityError
    with pytest.raises(IntegrityError):
        Review.objects.create(product=product, user=user, rating=5, comment='Second review')


@pytest.mark.django_db
def test_average_rating_calculation(product, user, another_user):
    Review.objects.create(product=product, user=user, rating=5, comment='Excellent')
    Review.objects.create(product=product, user=another_user, rating=3, comment='Good')

    reviews = Review.objects.filter(product=product)
    average = sum(r.rating for r in reviews) / len(reviews)
    assert average == 4.0


@pytest.mark.django_db
def test_review_string_representation(review):
    expected = f'Review by {review.user.username} for {review.product.name}'
    assert str(review) == expected


@pytest.mark.django_db
def test_review_ordering(product, user, another_user):
    review1 = Review.objects.create(product=product, user=user, rating=5, comment='First')
    review2 = Review.objects.create(product=product, user=another_user, rating=4, comment='Second')

    reviews = list(Review.objects.filter(product=product))
    assert reviews[0] == review2
    assert reviews[1] == review1


@pytest.mark.django_db
def test_review_update_existing(client, user, product):
    client.force_login(user)

    client.post(
        reverse('shop:product_detail', args=[product.id, product.slug]),
        {'rating': 3, 'comment': 'Initial review'}
    )

    client.post(
        reverse('shop:product_detail', args=[product.id, product.slug]),
        {'rating': 5, 'comment': 'Updated review'}
    )

    assert Review.objects.filter(product=product, user=user).count() == 1
    review = Review.objects.get(product=product, user=user)
    assert review.rating == 5
    assert review.comment == 'Updated review'


@pytest.mark.django_db
def test_review_requires_login(client, product):
    response = client.post(
        reverse('shop:product_detail', args=[product.id, product.slug]),
        {'rating': 5, 'comment': 'Test review'}
    )
    assert not Review.objects.filter(product=product).exists()
