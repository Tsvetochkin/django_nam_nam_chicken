import pytest
from django.urls import reverse
from decimal import Decimal
from shop.models import Category, Product


@pytest.mark.django_db
def test_list_products(client, product, unavailable_product):
    response = client.get(reverse('shop:product_list'))
    assert response.status_code == 200
    assert product.name in response.content.decode()
    assert unavailable_product.name not in response.content.decode()


@pytest.mark.django_db
def test_filter_by_category(client, category, product):
    another_category = Category.objects.create(name='Other Category', slug='other-category')
    other_product = Product.objects.create(
        category=another_category,
        name='Other Product',
        slug='other-product',
        price=Decimal('29.99'),
        stock=5,
        available=True
    )

    response = client.get(reverse('shop:product_list_by_category', args=[category.slug]))
    assert response.status_code == 200
    assert product.name in response.content.decode()
    assert other_product.name not in response.content.decode()


@pytest.mark.django_db
def test_search_products(client, product):
    response = client.get(reverse('shop:product_list'), {'q': 'Test'})
    assert response.status_code == 200
    assert product.name in response.content.decode()

    response = client.get(reverse('shop:product_list'), {'q': 'NonExistent'})
    assert product.name not in response.content.decode()


@pytest.mark.django_db
def test_search_in_description(client, product):
    response = client.get(reverse('shop:product_list'), {'q': 'description'})
    assert response.status_code == 200
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_product_detail(client, product):
    response = client.get(reverse('shop:product_detail', args=[product.id, product.slug]))
    assert response.status_code == 200
    assert product.name in response.content.decode()
    assert str(product.price) in response.content.decode()


@pytest.mark.django_db
def test_product_availability(client, unavailable_product):
    response = client.get(
        reverse('shop:product_detail', args=[unavailable_product.id, unavailable_product.slug])
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_product_stock(product):
    assert product.stock == 10
    product.stock = 0
    product.save()
    assert product.stock == 0


@pytest.mark.django_db
def test_category_creation(category):
    assert category.name == 'Test Category'
    assert category.slug == 'test-category'
    assert str(category) == 'Test Category'


@pytest.mark.django_db
def test_product_creation(product, category):
    assert product.name == 'Test Product'
    assert product.category == category
    assert product.available is True
    assert product.stock == 10
