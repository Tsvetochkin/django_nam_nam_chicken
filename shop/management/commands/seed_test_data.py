import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from shop.models import Category, Product, Coupon
from users.models import Profile
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Seeds comprehensive test data: users, products, coupons for Nam Nam Chicken.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting comprehensive test data seeding...'))

        # Create test users
        self.create_test_users()

        # Seed products
        self.seed_products()

        # Create coupons
        self.create_coupons()

        self.stdout.write(self.style.SUCCESS('Test data seeding completed!'))

    def create_test_users(self):
        self.stdout.write(self.style.SUCCESS('Creating test users...'))

        users_data = [
            {'username': 'admin', 'email': 'admin@namnam.com', 'password': 'admin123', 'is_staff': True, 'is_superuser': True},
            {'username': 'testuser', 'email': 'test@namnam.com', 'password': 'test123', 'is_staff': False, 'is_superuser': False},
            {'username': 'apro', 'email': 'apro@namnam.com', 'password': 'apro123', 'is_staff': False, 'is_superuser': False},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data['is_superuser'],
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User already exists: {user.username}'))

    def create_coupons(self):
        self.stdout.write(self.style.SUCCESS('Creating coupons...'))

        now = timezone.now()
        coupons_data = [
            {'code': 'WELCOME10', 'discount_percent': 10, 'valid_from': now, 'valid_to': now + timedelta(days=365), 'usage_limit': 100},
            {'code': 'VERANO20', 'discount_percent': 20, 'valid_from': now, 'valid_to': now + timedelta(days=90), 'usage_limit': 50},
            {'code': 'PROMO15', 'discount_percent': 15, 'valid_from': now, 'valid_to': now + timedelta(days=30), 'usage_limit': 30},
        ]

        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults={
                    'discount_percent': coupon_data['discount_percent'],
                    'valid_from': coupon_data['valid_from'],
                    'valid_to': coupon_data['valid_to'],
                    'active': True,
                    'usage_limit': coupon_data['usage_limit'],
                    'used_count': 0,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created coupon: {coupon.code} ({coupon.discount_percent}% off)'))
            else:
                self.stdout.write(self.style.WARNING(f'Coupon already exists: {coupon.code}'))

    def seed_products(self):
        self.stdout.write(self.style.SUCCESS('Seeding products...'))

        # Don't clear existing - just add/update
        menu_data = {
            'Alitas': [
                {'name': 'Alitas Clásicas (4 uds.)', 'description': 'Nuestras alitas fritas con el sazón original de la casa.', 'price': 5.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/FFC107/000000?text=Alitas+Clasicas'},
                {'name': 'Alitas Clásicas (6 uds.)', 'description': 'Un poco más de nuestras alitas con el sazón original.', 'price': 7.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/FFC107/000000?text=Alitas+Clasicas'},
                {'name': 'Alitas Clásicas (10 uds.)', 'description': 'El balde perfecto para compartir (o no).', 'price': 11.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/FFC107/000000?text=Alitas+Clasicas'},
                {'name': 'Alitas Picantes "Fuego" (4 uds.)', 'description': 'Un toque de fuego para los más atrevidos.', 'price': 5.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/DC3545/FFFFFF?text=Alitas+Picantes'},
                {'name': 'Alitas Picantes "Fuego" (6 uds.)', 'description': 'Más picante, más sabor.', 'price': 7.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/DC3545/FFFFFF?text=Alitas+Picantes'},
                {'name': 'Alitas Picantes "Fuego" (10 uds.)', 'description': '¿Te atreves a terminar el balde?', 'price': 11.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/DC3545/FFFFFF?text=Alitas+Picantes'},
                {'name': 'Alitas BBQ "Dulcemiel" (4 uds.)', 'description': 'Bañadas en nuestra salsa BBQ casera.', 'price': 5.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/6F4E37/FFFFFF?text=Alitas+BBQ'},
                {'name': 'Alitas BBQ "Dulcemiel" (6 uds.)', 'description': 'El balance perfecto entre dulce y ahumado.', 'price': 7.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/6F4E37/FFFFFF?text=Alitas+BBQ'},
                {'name': 'Alitas BBQ "Dulcemiel" (10 uds.)', 'description': 'Para los amantes de la BBQ.', 'price': 11.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/6F4E37/FFFFFF?text=Alitas+BBQ'},
            ],
            'Guarniciones': [
                {'name': 'Papas Fritas Clásicas', 'description': 'Papas fritas crujientes con sal marina.', 'price': 2.99, 'stock': 150, 'image_url': 'https://placehold.co/600x400/F4A460/000000?text=Papas+Fritas'},
                {'name': 'Papas Rústicas con Piel', 'description': 'Papas cortadas en gajos con piel y hierbas.', 'price': 3.49, 'stock': 150, 'image_url': 'https://placehold.co/600x400/8B4513/FFFFFF?text=Papas+Rusticas'},
                {'name': 'Aros de Cebolla', 'description': 'Aros de cebolla rebozados y fritos, extra crujientes.', 'price': 3.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/DAA520/000000?text=Aros+Cebolla'},
                {'name': 'Ensalada Coleslaw', 'description': 'Ensalada fresca de repollo con mayonesa cremosa.', 'price': 2.49, 'stock': 80, 'image_url': 'https://placehold.co/600x400/98FB98/000000?text=Coleslaw'},
            ],
            'Bebidas': [
                {'name': 'Coca-Cola (500ml)', 'description': 'Refresco clásico bien frío.', 'price': 1.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/DC143C/FFFFFF?text=Coca+Cola'},
                {'name': 'Sprite (500ml)', 'description': 'Refresco de lima-limón refrescante.', 'price': 1.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/00FF00/000000?text=Sprite'},
                {'name': 'Fanta (500ml)', 'description': 'Refresco de naranja burbujeante.', 'price': 1.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/FF8C00/000000?text=Fanta'},
                {'name': 'Agua Mineral (500ml)', 'description': 'Agua mineral sin gas.', 'price': 1.49, 'stock': 250, 'image_url': 'https://placehold.co/600x400/87CEEB/000000?text=Agua'},
                {'name': 'Jugo de Naranja Natural', 'description': 'Jugo de naranja recién exprimido.', 'price': 2.99, 'stock': 50, 'image_url': 'https://placehold.co/600x400/FFA500/000000?text=Jugo+Naranja'},
                {'name': 'Cerveza Artesanal (355ml)', 'description': 'Cerveza artesanal local tipo IPA.', 'price': 4.99, 'stock': 100, 'image_url': 'https://placehold.co/600x400/D2691E/FFFFFF?text=Cerveza'},
            ],
            'Salsas': [
                {'name': 'Salsa "Seúl Nocturno"', 'description': 'Salsa agridulce y profunda con un toque de gochujang. Inspirada en Seúl.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/4B0082/FFFFFF?text=Salsa+Seul'},
                {'name': 'Salsa "Original China" (Picante)', 'description': 'Salsa intensa y picante, inspirada en la cocina de Szechuan.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/B22222/FFFFFF?text=Salsa+China'},
                {'name': 'Salsa "De Argentina con Amor"', 'description': 'Nuestro chimichurri casero, fresco y lleno de sabor.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/008000/FFFFFF?text=Salsa+Argentina'},
                {'name': 'Salsa Ranch', 'description': 'Salsa cremosa estilo ranch, perfecta para dipear.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/F5F5DC/000000?text=Ranch'},
                {'name': 'Salsa de Ajo', 'description': 'Mayonesa con ajo fresco y especias.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/FFF8DC/000000?text=Salsa+Ajo'},
                {'name': 'Salsa Honey Mustard', 'description': 'Dulce y picante, ideal para todo.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/FFD700/000000?text=Honey+Mustard'},
            ],
        }

        for category_name, products_data in menu_data.items():
            category, created = Category.objects.get_or_create(name=category_name, slug=slugify(category_name))
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

            for product_data in products_data:
                product, created = Product.objects.get_or_create(
                    slug=slugify(product_data['name']),
                    defaults={
                        'category': category,
                        'name': product_data['name'],
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'stock': product_data['stock'],
                        'available': True
                    }
                )

                if created:
                    # Fetch and save image
                    try:
                        response = requests.get(product_data['image_url'], stream=True)
                        response.raise_for_status()
                        image_content = response.content
                        content_type = response.headers.get('Content-Type', '')

                        if content_type.startswith('image/') and len(image_content) >= 100:
                            image_name = slugify(product_data['name']) + '.png'
                            product.image.save(image_name, ContentFile(image_content), save=False)
                            product.save()
                            self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
                        else:
                            product.save()
                            self.stdout.write(self.style.WARNING(f'Created product without image: {product.name}'))
                    except Exception as e:
                        product.save()
                        self.stdout.write(self.style.WARNING(f'Created product without image: {product.name} ({e})'))
                else:
                    self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))
