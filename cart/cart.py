from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Ensure all prices are strings before saving to session
        for product_id in self.cart:
            if isinstance(self.cart[product_id]['price'], Decimal):
                self.cart[product_id]['price'] = str(self.cart[product_id]['price'])
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = []
        for id_str in self.cart.keys():
            try:
                product_ids.append(int(id_str))
            except ValueError:
                del self.cart[id_str]
                self.save()
        
        products = Product.objects.filter(id__in=product_ids)
        
        product_map = {str(p.id): p for p in products}

        cart_copy = self.cart.copy()
        for product_id, item in list(cart_copy.items()): # Iterate over a copy to allow modification
            print(f"DEBUG: Processing item - product_id: {product_id}, item: {item}")
            if product_id in product_map:
                item['product'] = product_map[product_id]
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                print(f"DEBUG: Yielding item with product: {item['product'].name}")
                yield item
            else:
                # Product no longer exists in the database, remove it from cart
                print(f"DEBUG: Product {product_id} not found in DB. Removing from cart.")
                del self.cart[product_id]
                self.save()


    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.cart = {} # Reset the cart attribute
        self.save()
