from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .views import (
    SignUpView, CustomLoginView, CustomLogoutView,
    CustomPasswordResetView, CustomPasswordResetConfirmView, upload_test
)

# ------------------------------
# DRF API Router
# ------------------------------
router = DefaultRouter()
router.register("categories", views.CategoryView, basename="category")
router.register("products", views.ProductView, basename="product")
router.register("reviews", views.ReviewView, basename="review")
router.register("orders", views.OrderView, basename="order")
router.register("addresses", views.AddressView, basename="address")
router.register("testimonials", views.TestimonialViewSet, basename="testimonial")
router.register("newsletter", views.NewsletterViewSet, basename="newsletter")
router.register("contacts", views.ContactMessageViewSet, basename="contact")

# ------------------------------
# URL Patterns
# ------------------------------
urlpatterns = [
    # ---------- Public pages ----------
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),

    # ---------- Cart ----------
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("search/", views.search_products, name="search_products"), 
    
    path("products/", views.product_list, name="products"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),

    # ---------- User Orders ----------
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:pk>/", views.order_detail, name="order_detail"),

    # ---------- Checkout ----------
    path("checkout/", views.checkout_view, name="checkout"),
    path("order/place/", views.place_order, name="place_order"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),

    # ---------- Auth (Custom) ----------
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # ---------- JWT ----------
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.MeView.as_view(), name="me"),

    # ---------- API Router ----------
    path("api/", include(router.urls)),
    
    # Newsletter
    path("subscribe/", views.subscribe_newsletter, name="subscribe_newsletter"),
    path("newsletter/", views.newsletter_page, name="newsletter_page"),

    # ---------- Product Image Upload ----------
    path(
        "api/products/<int:product_pk>/upload-image/",
        views.ProductImageUploadView.as_view({"post": "create"}),
        name="product_image_upload",
    ),
    path(
        "api/products/<int:product_pk>/delete-image/<int:pk>/",
        views.ProductImageUploadView.as_view({"delete": "destroy"}),
        name="product_image_delete",
    ),
    path("testimonials/", views.testimonials, name="testimonials"),

    path("upload-test/", upload_test, name="upload_test"),
]
