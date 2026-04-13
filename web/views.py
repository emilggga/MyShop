from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegisterForm
from .models import CartItem, Category, Favorite, Product


def apply_product_filters(request, products):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    price_from = request.GET.get("price_from", "").strip()
    price_to = request.GET.get("price_to", "").strip()
    in_stock = request.GET.get("in_stock")
    sale = request.GET.get("sale")
    sort = request.GET.get("sort", "").strip()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if price_from:
        try:
            products = products.filter(price__gte=Decimal(price_from))
        except (InvalidOperation, ValueError):
            pass

    if price_to:
        try:
            products = products.filter(price__lte=Decimal(price_to))
        except (InvalidOperation, ValueError):
            pass

    if in_stock == "1":
        products = products.filter(in_stock=True)

    if sale == "1":
        products = products.filter(discount_price__isnull=False)

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("-created_at")

    return products


def home(request):
    categories = Category.objects.all()
    products = Product.objects.select_related("category").all()
    products = apply_product_filters(request, products)

    return render(request, "web/home.html", {
        "categories": categories,
        "products": products,
    })


def category_detail(request, slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.select_related("category").filter(category=category)
    products = apply_product_filters(request, products)

    return render(request, "web/category_detail.html", {
        "categories": categories,
        "category": category,
        "products": products,
    })


def product_detail(request, slug):
    categories = Category.objects.all()
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()

    return render(request, "web/product_detail.html", {
        "categories": categories,
        "product": product,
        "related_products": related_products,
        "is_favorite": is_favorite,
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Регистрация прошла успешно.")
        return redirect("home")

    return render(request, "web/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "web/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = "home"


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 1},
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Товар добавлен в корзину.")
    return redirect("cart")


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    total = sum(item.total_price for item in cart_items)

    return render(request, "web/cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Товар удалён из корзины.")
    return redirect("cart")


@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    return render(request, "web/favorites.html", {"favorites": favorites})


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite = Favorite.objects.filter(user=request.user, product=product).first()

    if favorite:
        favorite.delete()
        messages.success(request, "Товар удалён из избранного.")
    else:
        Favorite.objects.create(user=request.user, product=product)
        messages.success(request, "Товар добавлен в избранное.")

    return redirect("product_detail", slug=product.slug)


def search_view(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category").all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query)
        )
    else:
        products = Product.objects.none()

    return render(request, "web/search.html", {
        "query": query,
        "products": products,
    })