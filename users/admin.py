from django.contrib import admin
from .models import Profile, WishlistItem

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'postal_code')
    search_fields = ('user__username', 'user__email', 'city')
    list_filter = ('city',)

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
