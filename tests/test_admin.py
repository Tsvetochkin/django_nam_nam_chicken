import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from shop.models import Product, Order, Coupon, Category, Review
from shop.admin import ProductAdmin, OrderAdmin, CouponAdmin, CategoryAdmin, ReviewAdmin


@pytest.mark.django_db
def test_product_admin_registered():
    assert admin.site.is_registered(Product)


@pytest.mark.django_db
def test_order_admin_registered():
    assert admin.site.is_registered(Order)


@pytest.mark.django_db
def test_coupon_admin_registered():
    assert admin.site.is_registered(Coupon)


@pytest.mark.django_db
def test_category_admin_registered():
    assert admin.site.is_registered(Category)


@pytest.mark.django_db
def test_review_admin_registered():
    assert admin.site.is_registered(Review)


@pytest.mark.django_db
def test_product_admin_list_display(product):
    site = AdminSite()
    product_admin = ProductAdmin(Product, site)

    assert 'name' in product_admin.list_display
    assert 'price' in product_admin.list_display
    assert 'stock' in product_admin.list_display
    assert 'available' in product_admin.list_display


@pytest.mark.django_db
def test_order_admin_list_display(order):
    site = AdminSite()
    order_admin = OrderAdmin(Order, site)

    assert 'id' in order_admin.list_display
    assert 'first_name' in order_admin.list_display
    assert 'email' in order_admin.list_display
    assert 'paid' in order_admin.list_display
    assert 'status' in order_admin.list_display


@pytest.mark.django_db
def test_coupon_admin_list_display(valid_coupon):
    site = AdminSite()
    coupon_admin = CouponAdmin(Coupon, site)

    assert 'code' in coupon_admin.list_display
    assert 'discount_percent' in coupon_admin.list_display
    assert 'active' in coupon_admin.list_display


@pytest.mark.django_db
def test_product_admin_editable_fields():
    site = AdminSite()
    product_admin = ProductAdmin(Product, site)

    assert 'price' in product_admin.list_editable
    assert 'stock' in product_admin.list_editable
    assert 'available' in product_admin.list_editable


@pytest.mark.django_db
def test_order_admin_editable_fields():
    site = AdminSite()
    order_admin = OrderAdmin(Order, site)

    assert 'status' in order_admin.list_editable
