from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile
from users.forms import UserRegistrationForm
from shop.models import Order, OrderItem, Product, Category
from decimal import Decimal




