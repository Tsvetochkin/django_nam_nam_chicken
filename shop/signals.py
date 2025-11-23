from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review, Product

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    reviews = Review.objects.filter(product=product)
    
    if reviews.exists():
        product.average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        product.total_reviews = reviews.count()
    else:
        product.average_rating = 0.00
        product.total_reviews = 0
    
    product.save()