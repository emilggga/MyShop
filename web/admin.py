from django.contrib import admin
from .models import Category, Product, CartItem, Favorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "discount_price",
        "in_stock",
        "is_new",
        "created_at",
    )
    list_filter = ("category", "in_stock", "is_new", "created_at")
    list_editable = ("price", "discount_price", "in_stock", "is_new")
    search_fields = ("name", "description", "short_description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "product__name")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "product__name")