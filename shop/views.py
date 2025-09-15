from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import TestimonialForm
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import NewsletterSubscription
from django import forms
from django.shortcuts import render
from django.conf import settings


from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
)
from django.views.generic import CreateView

# Forms
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm,
    CustomPasswordResetForm, CustomSetPasswordForm,
)

# Models
from .models import (
    CustomUser, Category, Product, ProductImage, Review,
    Order, OrderItem, Address, NewsletterSubscription,
    ContactMessage, Testimonial, SiteConfig
)

# Cart
from .cart import Cart

# DRF
from rest_framework import viewsets, permissions, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import OrderingFilter

# Serializers
from .serializers import (
    CategorySerializer, ProductSerializer, ProductImageSerializer,
    ReviewSerializer, OrderSerializer, AddressSerializer,
    NewsletterSubscriptionSerializer, ContactMessageSerializer,
    TestimonialSerializer
)

# -------------------------------------------------------------------
# AUTH VIEWS
# -------------------------------------------------------------------

class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Account created successfully 🎉")
        return redirect("home")


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # Staff/admin → Django admin dashboard (Jazzmin)
            return reverse_lazy("admin:index")
        # Normal customer → homepage (you can switch to "my_orders" if preferred)
        return reverse_lazy("home")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("login")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("login")


# -------------------------------------------------------------------
# PUBLIC SHOP VIEWS
# -------------------------------------------------------------------

def home(request):
    featured_products = Product.objects.filter(featured=True)[:6]
    categories = Category.objects.all()
    testimonials = Testimonial.objects.order_by("-created_at")[:4]  # show only 4 latest
    site_config = SiteConfig.objects.first()

    return render(request, "shop/home.html", {
        "featured_products": featured_products,
        "categories": categories,
        "testimonials": testimonials,
        "site_config": site_config,
    })


def product_list(request):
    products = Product.objects.all().order_by("-created_at")
    return render(request, "shop/product_list.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = Review.objects.filter(product=product).select_related("user")
    return render(request, "shop/product.html", {"product": product, "reviews": reviews})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).order_by("-created_at")
    return render(request, "shop/category_products.html", {
        "category": category,
        "products": products,
    })


def contact(request):
    return render(request, "shop/contact.html")
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Product
from .cart import Cart


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart and redirect back to previous page or cart detail."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get("quantity", 1))
    override = str(request.POST.get("override", "")).lower() in ["true", "1", "yes"]

    cart.add(product=product, quantity=quantity, override_quantity=override)
    request.session.modified = True  # ensure cart persists

    # ✅ Redirect back to same page (fallback to cart detail)
    return redirect(request.META.get("HTTP_REFERER", reverse("cart_detail")))


@require_POST
def remove_from_cart(request, product_id):
    """Remove product from cart and redirect to cart detail."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart.remove(product)
    request.session.modified = True

    return redirect("cart_detail")


def cart_detail(request):
    """Display cart contents."""
    cart = Cart(request)
    return render(request, "shop/cart_detail.html", {
        "cart": cart,
        "total_savings": cart.get_total_savings(),
    })

#---------------------------------------------------------------
# CHECKOUT & ORDERS
# -------------------------------------------------------------------

@login_required
def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart_detail")

    # Prepare cart items with absolute image URLs
    cart_items = []
    for item in cart:
        product = item["product"]
        image_url = None
        first_image = getattr(product.images.first(), "image", None)
        if first_image:
            image_url = request.build_absolute_uri(first_image.url)

        cart_items.append({
            "product": product,
            "quantity": item["quantity"],
            "price": item["price"],
            "total_price": item["total_price"],
            "image_url": image_url,
        })

    addresses = Address.objects.filter(user=request.user)
    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "addresses": addresses,
        "total": cart.get_total_price(),
    })


@login_required
def place_order(request):
    """
    Create an order from the user's cart.
    Supports selecting an existing address or creating a new one.
    """
    cart = Cart(request)

    if request.method == "POST":
        if len(cart) == 0:
            messages.warning(request, "Your cart is empty.")
            return redirect("cart_detail")

        # ---------- Handle address ----------
        address_id = request.POST.get("address_id")
        if address_id:
            # Use existing address
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            # Create new address
            address = Address.objects.create(
                user=request.user,
                full_name=request.POST.get("full_name", request.user.get_full_name()),
                phone=request.POST.get("phone", ""),
                line1=request.POST.get("line1", ""),
                line2=request.POST.get("line2", ""),
                city=request.POST.get("city", ""),
                notes=request.POST.get("notes", ""),
            )

        # ---------- Create Order ----------
        order = Order.objects.create(
            user=request.user,
            address=address,
            whatsapp_number=request.POST.get("whatsapp_number", ""),
            total=cart.get_total_price(),
            status="new",
        )

        # ---------- Add Order Items ----------
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                qty=item["quantity"],
                price_each=item["product"].price,
            )

        # Clear cart
        cart.clear()

        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect("order_success", order_id=order.id)

    return redirect("checkout_view")


@login_required
def order_success(request, order_id):
    """
    Success page after placing an order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})


@login_required
def my_orders(request):
    """
    List all orders for the logged-in user.
    """
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "shop/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    """
    Show details of a single order.
    """
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "shop/order_detail.html", {"order": order})

# -------------------------------------------------------------------
# SEARCH
# -------------------------------------------------------------------

def search_products(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.all()

    return render(request, "shop/search.html", {
        "products": products,
        "query": query,
        "categories": categories,
        "selected_category": category_slug,
    })


# -------------------------------------------------------------------
# API VIEWS (DRF)
# -------------------------------------------------------------------

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
            "email": user.email,
        })


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("images").all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "watts", "created_at"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if cat := params.get("category"):
            qs = qs.filter(category__slug=cat)
        if watts_min := params.get("watts_min"):
            qs = qs.filter(watts__gte=watts_min)
        if price_min := params.get("price_min"):
            qs = qs.filter(price__gte=price_min)
        if price_max := params.get("price_max"):
            qs = qs.filter(price__lte=price_max)
        return qs

    @action(detail=False, methods=["get"])
    def featured(self, request):
        qs = self.get_queryset().filter(featured=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ReviewView(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("product", "user").all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AddressView(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by("-created_at")


class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by("-created_at")
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class ProductImageUploadView(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, product_pk=None):
        product = get_object_or_404(Product, pk=product_pk)
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, product_pk=None, pk=None):
        image = get_object_or_404(ProductImage, pk=pk, product_id=product_pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all().order_by("-created_at")
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]


class NewsletterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [AllowAny]


class ContactMessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]


# -------------------------------------------------------------------
# ERROR HANDLERS
# -------------------------------------------------------------------

def handle_404(request, exception):
    return render(request, "shop/not_found.html", status=404)


def handle_500(request):
    return render(request, "shop/500.html", status=500)






def testimonials(request):
    testimonials = Testimonial.objects.all().order_by("-created_at")

    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your feedback! 🎉")
            return redirect("testimonials")
    else:
        form = TestimonialForm()

    return render(request, "shop/testimonials.html", {
        "testimonials": testimonials,
        "form": form,
    })


def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            obj, created = NewsletterSubscription.objects.get_or_create(email=email)
            if created:
                messages.success(request, "You have been subscribed successfully!")
            else:
                messages.info(request, "You are already subscribed.")
        else:
            messages.error(request, "Please provide a valid email address.")
    return redirect(request.META.get("HTTP_REFERER", "home"))


def newsletter_page(request):
    return render(request, "shop/newsletter.html")



#############################################
# Simple form with an image field


class UploadTestForm(forms.Form):
    image = forms.ImageField()

def upload_test(request):
    url = None
    if request.method == "POST":
        form = UploadTestForm(request.POST, request.FILES)
        if form.is_valid():
            # Save directly using default storage (Cloudinary)
            image = form.cleaned_data["image"]
            from django.core.files.storage import default_storage
            path = default_storage.save(image.name, image)
            url = default_storage.url(path)
    else:
        form = UploadTestForm()

    return render(request, "shop/upload_test.html", {"form": form, "url": url})