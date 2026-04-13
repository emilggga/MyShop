from django.urls import path
from .views import (
    home,
    category_detail,
    product_detail,
    register_view,
    CustomLoginView,
    CustomLogoutView,
    cart_view,
    add_to_cart,
    remove_from_cart,
    favorites_view,
    toggle_favorite,
    search_view,
)

urlpatterns = [
    path("", home, name="home"),
    path("search/", search_view, name="search"),

    path("category/<slug:slug>/", category_detail, name="category_detail"),
    path("product/<slug:slug>/", product_detail, name="product_detail"),

    path("register/", register_view, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    path("cart/", cart_view, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),

    path("favorites/", favorites_view, name="favorites"),
    path("favorites/toggle/<int:product_id>/", toggle_favorite, name="toggle_favorite"),
]