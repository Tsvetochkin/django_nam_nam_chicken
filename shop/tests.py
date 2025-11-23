from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from shop.models import Category, Product, Order, OrderItem
from cart.cart import Cart
from users.models import Profile # Import Profile model for user tests

class ShopModelTest(TestCase):
    """Tests for the shop app models."""

    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='This is a test product.',
            price=Decimal('19.99'),
            stock=10,
            available=True
        )
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_category_creation(self):
        """Test Category model creation and string representation."""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertEqual(str(self.category), 'Test Category')
        self.assertEqual(self.category.get_absolute_url(), reverse('shop:product_list_by_category', args=['test-category']))

    def test_product_creation(self):
        """Test Product model creation and string representation."""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.slug, 'test-product')
        self.assertEqual(self.product.price, Decimal('19.99'))
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(str(self.product), 'Test Product')
        self.assertEqual(self.product.get_absolute_url(), reverse('shop:product_detail', args=[self.product.id, 'test-product']))

    def test_order_creation(self):
        """Test Order model creation and total cost calculation."""
        order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            address='123 Test St',
            celular='1234567890'
        )
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.user, self.user)
        self.assertEqual(str(order), f'Order {order.id}')

        OrderItem.objects.create(order=order, product=self.product, price=self.product.price, quantity=2)
        self.assertEqual(order.get_total_cost(), Decimal('39.98'))

    def test_order_item_creation(self):
        """Test OrderItem model creation and cost calculation."""
        order = Order.objects.create(
            user=self.user,
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            address='456 Test Ave',
            celular='0987654321'
        )
        order_item = OrderItem.objects.create(order=order, product=self.product, price=self.product.price, quantity=3)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 3)
        self.assertEqual(order_item.get_cost(), Decimal('59.97'))

class ShopViewTest(TestCase):
    """Tests for the shop app views."""

    def setUp(self):
        self.client = Client()
        self.session = self.client.session
        self.session[settings.CART_SESSION_ID] = {}
        self.session.save()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product1 = Product.objects.create(
            category=self.category, name='Product A', slug='product-a', price=Decimal('10.00'), stock=5, available=True
        )
        self.product2 = Product.objects.create(
            category=self.category, name='Product B', slug='product-b', price=Decimal('20.00'), stock=0, available=False
        )
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_product_list_view(self):
        """Test product_list view displays available products."""
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product A')
        self.assertNotContains(response, 'Product B') # Not available

    def test_product_list_by_category_view(self):
        """Test product_list view filters by category."""
        response = self.client.get(reverse('shop:product_list_by_category', args=['test-category']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product A')

    def test_product_list_search(self):
        """Test product_list view with search query."""
        response = self.client.get(reverse('shop:product_list') + '?q=Product+A')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product A')
        self.assertNotContains(response, 'Product B')

    def test_product_detail_view(self):
        """Test product_detail view displays product details."""
        response = self.client.get(reverse('shop:product_detail', args=[self.product1.id, self.product1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product A')
        self.assertContains(response, 'Añadir al Carrito') # Check button text

    def test_order_create_view_get(self):
        """Test order_create view displays form for GET request."""
        # Add product to cart using cart_add view
        self.client.post(reverse('cart:cart_add', args=[self.product1.id]), {
            'quantity': 1,
            'update': False
        })
        response = self.client.get(reverse('shop:order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Realizar Pedido') # Check button text

    def test_order_create_view_post_anonymous(self):
        # Add product to cart using cart_add view
        self.client.post(reverse('cart:cart_add', args=[self.product1.id]), {
            'quantity': 1,
            'update': False
        })
        response = self.client.post(reverse('shop:order_create'), {
            'first_name': 'Anon',
            'last_name': 'User',
            'email': 'anon@example.com',
            'address': 'Anon Street',
            'celular': '1112223334'
        })
        self.assertEqual(response.status_code, 200) # Renders created.html
        self.assertContains(response, 'Su pedido ha sido realizado con éxito')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        cart = Cart(self.client) # Re-initialize cart to get updated state
        self.assertEqual(len(cart), 0) # Cart should be cleared
    def test_order_create_view_post_authenticated(self):
        """Test order_create view processes POST request for authenticated user."""
        self.client.login(username='testuser', password='testpassword')
        # Add product to cart using cart_add view
        self.client.post(reverse('cart:cart_add', args=[self.product1.id]), {
            'quantity': 1,
            'update': False
        })
        response = self.client.post(reverse('shop:order_create'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': 'User Address',
            'celular': '5556667778'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Su pedido ha sido realizado con éxito')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().user, self.user)
        cart = Cart(self.client) # Re-initialize cart to get updated state
        self.assertEqual(len(cart), 0)
    def test_order_create_view_empty_cart(self):
        """Test order_create view redirects if cart is empty."""
        response = self.client.get(reverse('shop:order_create'))
        self.assertRedirects(response, reverse('shop:product_list'))

class CartTest(TestCase):
    """Tests for the cart app functionality."""

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

    def test_cart_add(self):
        """Test adding a product to the cart."""
        self.cart.add(product=self.product, quantity=2)
        self.assertEqual(len(self.cart), 2)
        self.assertEqual(self.cart.get_total_price(), Decimal('50.00'))

    def test_cart_update_quantity(self):
        """Test updating product quantity in the cart."""
        self.cart.add(product=self.product, quantity=2)
        self.cart.add(product=self.product, quantity=3, update_quantity=True)
        self.assertEqual(len(self.cart), 3)
        self.assertEqual(self.cart.get_total_price(), Decimal('75.00'))

    def test_cart_remove(self):
        """Test removing a product from the cart."""
        self.cart.add(product=self.product, quantity=2)
        self.cart.remove(product=self.product)
        self.assertEqual(len(self.cart), 0)

    def test_cart_clear(self):
        """Test clearing the entire cart."""
        self.cart.add(product=self.product, quantity=5)
        self.cart.clear()
        self.assertEqual(len(self.cart), 0)

    def test_cart_iter(self):
        """Test cart iteration and product details."""
        self.cart.add(product=self.product, quantity=2)
        items = list(self.cart)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['product'], self.product)
        self.assertEqual(items[0]['quantity'], 2)
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



class ManagementCommandTest(TestCase):
    """Tests for custom management commands."""

    def test_seed_products_command(self):
        """Test the seed_products command populates the database."""
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)

        # Call the management command
        from django.core.management import call_command
        call_command('seed_products')

        self.assertGreater(Category.objects.count(), 0)
        self.assertGreater(Product.objects.count(), 0)
        self.assertEqual(Category.objects.get(name='Alitas').slug, 'alitas')
        self.assertEqual(Product.objects.get(name='Alitas Clásicas (4 uds.)').slug, 'alitas-clasicas-4-uds')