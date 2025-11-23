from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from shop.models import Product, Category
from cart.cart import Cart
from cart.forms import CartAddProductForm

class CartClassTest(TestCase):
    """Tests for the Cart class functionality."""

    def setUp(self):
        self.client = Client()
        self.session = self.client.session
        self.session[settings.CART_SESSION_ID] = {}
        self.session.save()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            category=self.category, name='Cart Product', slug='cart-product', price=Decimal('25.00'), stock=10, available=True
        )
        self.cart = Cart(self.client)

    def test_cart_initialization(self):
        """Test cart is initialized correctly."""
        self.assertIn(settings.CART_SESSION_ID, self.session)
        self.assertEqual(self.session[settings.CART_SESSION_ID], {})

    def test_cart_add_new_product(self):
        """Test adding a new product to the cart."""
        self.cart.add(product=self.product, quantity=2)
        self.assertEqual(len(self.cart), 2)
        self.assertEqual(self.cart.cart[str(self.product.id)]['quantity'], 2)
        self.assertEqual(self.cart.cart[str(self.product.id)]['price'], str(self.product.price))

    def test_cart_add_existing_product(self):
        """Test adding an existing product increases quantity."""
        self.cart.add(product=self.product, quantity=2)
        self.cart.add(product=self.product, quantity=3)
        self.assertEqual(len(self.cart), 5)
        self.assertEqual(self.cart.cart[str(self.product.id)]['quantity'], 5)

    def test_cart_update_quantity(self):
        """Test updating product quantity in the cart."""
        self.cart.add(product=self.product, quantity=2)
        self.cart.add(product=self.product, quantity=5, update_quantity=True)
        self.assertEqual(len(self.cart), 5)
        self.assertEqual(self.cart.cart[str(self.product.id)]['quantity'], 5)

    def test_cart_remove_product(self):
        """Test removing a product from the cart."""
        self.cart.add(product=self.product, quantity=2)
        self.cart.remove(product=self.product)
        self.assertEqual(len(self.cart), 0)
        self.assertNotIn(str(self.product.id), self.cart.cart)

    def test_cart_clear(self):
        """Test clearing the entire cart."""
        self.cart.add(product=self.product, quantity=5)
        self.cart.clear()
        self.client.session.load() # Reload the session
        self.assertEqual(len(self.cart), 0)

    def test_cart_get_total_price(self):
        """Test calculating the total price of items in the cart."""
        self.cart.add(product=self.product, quantity=2)
        self.assertEqual(self.cart.get_total_price(), Decimal('50.00'))

    def test_cart_iter(self):
        """Test cart iteration and product details."""
        self.cart.add(product=self.product, quantity=2)
        items = list(self.cart)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['product'], self.product)
        self.assertEqual(items[0]['quantity'], 2)
        self.assertEqual(items[0]['price'], Decimal('25.00'))
        self.assertEqual(items[0]['total_price'], Decimal('50.00'))

    def test_cart_iter_deleted_product(self):
        """Test cart iteration handles deleted products gracefully."""
        self.cart.add(product=self.product, quantity=1)
        product_id = self.product.id
        self.product.delete() # Delete product from DB

        # Re-initialize cart to ensure session is loaded
        cart_after_delete = Cart(self.client)
        items = list(cart_after_delete) # This should trigger __iter__ and clean up
        self.assertEqual(len(items), 0)
        self.assertEqual(len(cart_after_delete), 0) # Cart should be empty

class CartViewTest(TestCase):
    """Tests for the cart app views."""

    def setUp(self):
        self.client = Client()
        self.session = self.client.session
        self.session[settings.CART_SESSION_ID] = {}
        self.session.save()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            category=self.category, name='View Product', slug='view-product', price=Decimal('15.00'), stock=10, available=True
        )

    def test_cart_detail_view(self):
        """Test cart_detail view displays cart contents."""
        # Add product to cart using cart_add view
        response = self.client.post(reverse('cart:cart_add', args=[self.product.id]), {
            'quantity': 2,
            'update': False
        })
        self.assertRedirects(response, reverse('cart:cart_detail'))

        # Now get the cart detail view
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'View Product')
        self.assertContains(response, '30.00') # Total price

    def test_cart_add_view(self):
        """Test cart_add view adds product to cart."""
        response = self.client.post(reverse('cart:cart_add', args=[self.product.id]), {'quantity': 1, 'update': False})
        self.assertRedirects(response, reverse('cart:cart_detail'))
        cart = Cart(self.client)
        self.assertEqual(len(cart), 1)

    def test_cart_remove_view(self):
        """Test cart_remove view removes product from cart."""
        cart = Cart(self.client)
        cart.add(product=self.product, quantity=1)
        response = self.client.post(reverse('cart:cart_remove', args=[self.product.id])) # Use POST as view is @require_POST
        self.assertRedirects(response, reverse('cart:cart_detail'))
        cart = Cart(self.client) # Re-initialize cart to get updated state
        self.assertEqual(len(cart), 0)

    def test_cart_clear_view(self):
        """Test cart_clear view clears the cart."""
        cart = Cart(self.client)
        cart.add(product=self.product, quantity=3)
        response = self.client.post(reverse('cart:cart_clear'))
        self.assertRedirects(response, reverse('cart:cart_detail'))
        cart = Cart(self.client) # Re-initialize cart to get updated state
        self.assertEqual(len(cart), 0)

class CartFormTest(TestCase):
    """Tests for cart forms."""

    def test_cart_add_product_form_valid(self):
        """Test CartAddProductForm with valid data."""
        form = CartAddProductForm(data={'quantity': 1, 'update': False})
        self.assertTrue(form.is_valid())

    def test_cart_add_product_form_invalid_quantity(self):
        """Test CartAddProductForm with invalid quantity."""
        form = CartAddProductForm(data={'quantity': 0, 'update': False})
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)