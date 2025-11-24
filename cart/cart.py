from decimal import Decimal
from django.conf import settings
from shop.models import Product, Coupon


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
        self.coupon_id = self.session.get('coupon_id')

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
        for product_id, item in list(cart_copy.items()):
            if product_id in product_map:
                item['product'] = product_map[product_id]
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item
            else:
                # Product no longer exists in the database, remove it from cart
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
        self.cart = {}
        self.clear_coupon()
        self.save()

    def apply_coupon(self, coupon):
        self.session['coupon_id'] = coupon.id
        self.coupon_id = coupon.id
        self.session.modified = True

    def clear_coupon(self):
        if 'coupon_id' in self.session:
            del self.session['coupon_id']
        self.coupon_id = None
        self.session.modified = True

    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.filter(id=self.coupon_id).first()
        return None

    def get_discount(self):
        if self.coupon:
            return self.get_total_price() * (Decimal(self.coupon.discount_percent) / Decimal(100))
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
