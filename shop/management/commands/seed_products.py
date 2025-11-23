import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from shop.models import Category, Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds the database with initial product data for Nam Nam Chicken.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding for Nam Nam Chicken...'))

        # Clear existing data to ensure idempotency
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing products and categories.'))

        # Define the menu data
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
            'Muslos': [
                {'name': 'Muslo Crujiente (1 ud.)', 'description': 'Un muslo de pollo jugoso con nuestra cobertura extra crujiente.', 'price': 3.49, 'stock': 50, 'image_url': 'https://placehold.co/600x400/FFD700/000000?text=Muslo+Crujiente'},
                {'name': 'Combo Muslos (2 uds.)', 'description': 'Dos muslos de pollo para un apetito más grande.', 'price': 6.49, 'stock': 50, 'image_url': 'https://placehold.co/600x400/FFD700/000000?text=Combo+Muslos'},
            ],
            'Tiras de Pollo': [
                {'name': 'Tiras de Pollo (3 uds.)', 'description': 'Tiernas tiras de pechuga de pollo, perfectas para dipear.', 'price': 4.99, 'stock': 75, 'image_url': 'https://placehold.co/600x400/FF8C00/FFFFFF?text=Tiras+Pollo'},
                {'name': 'Tiras de Pollo (5 uds.)', 'description': 'Más tiras para más diversión.', 'price': 7.49, 'stock': 75, 'image_url': 'https://placehold.co/600x400/FF8C00/FFFFFF?text=Tiras+Pollo'},
            ],
            'Combos Mixtos': [
                {'name': 'Combo "El Probador" (3 pzs)', 'description': 'Prueba un poco de todo: 1 alita, 1 muslo, 1 tira.', 'price': 6.99, 'stock': 40, 'image_url': 'https://placehold.co/600x400/90EE90/000000?text=Combo+Probador'},
                {'name': 'Combo "El Hambriento" (5 pzs)', 'description': 'Para los que no se deciden: 2 alitas, 1 muslo, 2 tiras.', 'price': 9.99, 'stock': 40, 'image_url': 'https://placehold.co/600x400/90EE90/000000?text=Combo+Hambriento'},
            ],
            'Salsas': [
                {'name': 'Salsa "Seúl Nocturno"', 'description': 'Salsa agridulce y profunda con un toque de gochujang. Inspirada en Seúl.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/4B0082/FFFFFF?text=Salsa+Seul'},
                {'name': 'Salsa "Original China" (Picante)', 'description': 'Salsa intensa y picante, inspirada en la cocina de Szechuan.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/B22222/FFFFFF?text=Salsa+China'},
                {'name': 'Salsa "De Argentina con Amor"', 'description': 'Nuestro chimichurri casero, fresco y lleno de sabor.', 'price': 0.99, 'stock': 200, 'image_url': 'https://placehold.co/600x400/008000/FFFFFF?text=Salsa+Argentina'},
            ],
        }

        for category_name, products_data in menu_data.items():
            category, created = Category.objects.get_or_create(name=category_name, slug=slugify(category_name))
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))

            for product_data in products_data:
                product = Product(
                    category=category,
                    name=product_data['name'],
                    slug=slugify(product_data['name']),
                    description=product_data['description'],
                    price=product_data['price'],
                    stock=product_data['stock'],
                    available=True
                )

                # Fetch and save image
                try:
                    response = requests.get(product_data['image_url'], stream=True)
                    response.raise_for_status() # Raise an exception for HTTP errors

                    image_content = response.content # Read content fully

                    # Check if the response is actually an image and has reasonable size
                    content_type = response.headers.get('Content-Type', '')
                    if not content_type.startswith('image/') or len(image_content) < 100: # Check size
                        self.stdout.write(self.style.ERROR(f'URL content for {product.name} is not a valid image or too small: Content-Type={content_type}, Size={len(image_content)} bytes'))
                        product.image = None # Set image to None if not valid
                    else:
                        image_name = slugify(product_data['name']) + '.png'
                        # Use ContentFile with the fully read content
                        product.image.save(image_name, ContentFile(image_content), save=False)
                        self.stdout.write(self.style.SUCCESS(f'Fetched and prepared image for {product.name}'))
                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.ERROR(f'Could not fetch image for {product.name} from {product_data["image_url"]}: {e}'))
                    product.image = None # Set image to None on fetch error
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'An unexpected error occurred while processing image for {product.name}: {e}'))
                    product.image = None # Set image to None on other errors

                product.save()
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

