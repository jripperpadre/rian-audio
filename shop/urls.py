from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import dashboard_views as dash
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

    path("upload-test/", staff_member_required(upload_test), name="upload_test"),
]

# ──────────────────────────────
# Dashboard URLs
# ──────────────────────────────
dashboard_urls = [
    path("", dash.DashboardHome.as_view(), name="home"),
    path("products/", dash.ProductList.as_view(), name="product_list"),
    path("products/add/", dash.ProductCreate.as_view(), name="product_create"),
    path("products/<int:pk>/edit/", dash.ProductUpdate.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", dash.product_delete, name="product_delete"),
    path("categories/", dash.CategoryList.as_view(), name="category_list"),
    path("categories/add/", dash.CategoryCreate.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", dash.CategoryUpdate.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", dash.category_delete, name="category_delete"),
    path("orders/", dash.OrderList.as_view(), name="order_list"),
    path("orders/<int:pk>/", dash.OrderDetail.as_view(), name="order_detail"),
    path("orders/<int:pk>/status/", dash.order_update_status, name="order_update_status"),
    path("reviews/", dash.ReviewList.as_view(), name="review_list"),
    path("reviews/<int:pk>/delete/", dash.review_delete, name="review_delete"),
    path("testimonials/", dash.TestimonialList.as_view(), name="testimonial_list"),
    path("testimonials/add/", dash.TestimonialCreate.as_view(), name="testimonial_create"),
    path("testimonials/<int:pk>/edit/", dash.TestimonialUpdate.as_view(), name="testimonial_update"),
    path("testimonials/<int:pk>/delete/", dash.testimonial_delete, name="testimonial_delete"),
    path("contacts/", dash.ContactList.as_view(), name="contact_list"),
    path("contacts/<int:pk>/delete/", dash.contact_delete, name="contact_delete"),
    path("newsletter/", dash.NewsletterList.as_view(), name="newsletter_list"),
    path("newsletter/<int:pk>/delete/", dash.newsletter_delete, name="newsletter_delete"),
    path("site-config/", dash.site_config_edit, name="site_config"),
    path("users/", dash.UserList.as_view(), name="user_list"),
]

urlpatterns += [
    path("dashboard/", include((dashboard_urls, "shop"), namespace="dashboard")),
]
