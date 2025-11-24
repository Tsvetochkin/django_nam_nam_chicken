from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('order/create/', views.order_create, name='order_create'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment-failure/<int:order_id>/', views.payment_failure, name='payment_failure'),
    path('payment-pending/<int:order_id>/', views.payment_pending, name='payment_pending'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]
