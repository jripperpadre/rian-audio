from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.contrib.auth import get_user_model

from .models import (
    Product, Category, ProductImage, Review, Order, OrderItem,
    Address, NewsletterSubscription, ContactMessage, Testimonial, SiteConfig
)
from .forms import TestimonialForm

User = get_user_model()

staff_member = staff_member_required(login_url="login")


class DashboardMixin:
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_staff:
            return redirect("login")
        return super().dispatch(*args, **kwargs)


@method_decorator(staff_member, name="dispatch")
class DashboardHome(DashboardMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_products"] = Product.objects.count()
        ctx["total_categories"] = Category.objects.count()
        ctx["total_orders"] = Order.objects.count()
        ctx["total_revenue"] = Order.objects.filter(
            status__in=["sent", "done"]
        ).aggregate(t=Sum("total"))["t"] or 0
        ctx["total_users"] = User.objects.count()
        ctx["total_contacts"] = ContactMessage.objects.count()
        ctx["total_subscribers"] = NewsletterSubscription.objects.count()
        ctx["total_testimonials"] = Testimonial.objects.count()
        ctx["total_reviews"] = Review.objects.count()
        ctx["order_status_counts"] = Order.objects.values("status").annotate(
            c=Count("id")
        ).order_by("status")
        ctx["recent_orders"] = Order.objects.select_related("user", "address").order_by("-created_at")[:10]
        ctx["low_stock"] = Product.objects.filter(stock__lt=5).order_by("stock")[:10]
        ctx["recent_contacts"] = ContactMessage.objects.order_by("-created_at")[:5]
        return ctx


# ──────────────────────────────────────────────
# PRODUCTS
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class ProductList(DashboardMixin, ListView):
    model = Product
    template_name = "dashboard/product_list.html"
    context_object_name = "products"
    paginate_by = 25
    queryset = Product.objects.select_related("category").prefetch_related("images").order_by("-created_at")


@method_decorator(staff_member, name="dispatch")
class ProductCreate(DashboardMixin, CreateView):
    model = Product
    template_name = "dashboard/product_form.html"
    fields = ["name", "description", "price", "old_price", "watts", "category",
              "main_image", "featured", "stock", "badge_type", "whatsapp_number"]
    success_url = "/dashboard/products/"

    def form_valid(self, form):
        messages.success(self.request, "Product created successfully")
        return super().form_valid(form)


@method_decorator(staff_member, name="dispatch")
class ProductUpdate(DashboardMixin, UpdateView):
    model = Product
    template_name = "dashboard/product_form.html"
    fields = ["name", "description", "price", "old_price", "watts", "category",
              "main_image", "featured", "stock", "badge_type", "whatsapp_number"]
    success_url = "/dashboard/products/"

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully")
        return super().form_valid(form)


@require_POST
@staff_member
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted successfully")
    return redirect("dashboard:product_list")


# ──────────────────────────────────────────────
# CATEGORIES
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class CategoryList(DashboardMixin, ListView):
    model = Category
    template_name = "dashboard/category_list.html"
    context_object_name = "categories"
    queryset = Category.objects.annotate(product_count=Count("products")).order_by("name")


@method_decorator(staff_member, name="dispatch")
class CategoryCreate(DashboardMixin, CreateView):
    model = Category
    template_name = "dashboard/category_form.html"
    fields = ["name", "image"]
    success_url = "/dashboard/categories/"

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully")
        return super().form_valid(form)


@method_decorator(staff_member, name="dispatch")
class CategoryUpdate(DashboardMixin, UpdateView):
    model = Category
    template_name = "dashboard/category_form.html"
    fields = ["name", "image"]
    success_url = "/dashboard/categories/"

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully")
        return super().form_valid(form)


@require_POST
@staff_member
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.products.exists():
        messages.error(request, "Cannot delete category with existing products")
    else:
        category.delete()
        messages.success(request, "Category deleted successfully")
    return redirect("dashboard:category_list")


# ──────────────────────────────────────────────
# ORDERS
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class OrderList(DashboardMixin, ListView):
    model = Order
    template_name = "dashboard/order_list.html"
    context_object_name = "orders"
    paginate_by = 25
    queryset = Order.objects.select_related("user", "address").prefetch_related(
        "items__product"
    ).order_by("-created_at")


@method_decorator(staff_member, name="dispatch")
class OrderDetail(DashboardMixin, DetailView):
    model = Order
    template_name = "dashboard/order_detail.html"
    context_object_name = "order"
    queryset = Order.objects.select_related("user", "address").prefetch_related(
        "items__product"
    )


@require_POST
@staff_member
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get("status")
    valid_statuses = dict(Order.STATUS_CHOICES)
    if new_status in valid_statuses:
        order.status = new_status
        order.save(update_fields=["status"])
        messages.success(request, f"Order #{order.id} status changed to {valid_statuses[new_status]}")
    else:
        messages.error(request, "Invalid status")
    return redirect("dashboard:order_detail", pk=pk)


# ──────────────────────────────────────────────
# REVIEWS
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class ReviewList(DashboardMixin, ListView):
    model = Review
    template_name = "dashboard/review_list.html"
    context_object_name = "reviews"
    paginate_by = 25
    queryset = Review.objects.select_related("product", "user").order_by("-created_at")


@require_POST
@staff_member
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, "Review deleted successfully")
    return redirect("dashboard:review_list")


# ──────────────────────────────────────────────
# TESTIMONIALS
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class TestimonialList(DashboardMixin, ListView):
    model = Testimonial
    template_name = "dashboard/testimonial_list.html"
    context_object_name = "testimonials"
    queryset = Testimonial.objects.order_by("-created_at")


@method_decorator(staff_member, name="dispatch")
class TestimonialCreate(DashboardMixin, CreateView):
    model = Testimonial
    template_name = "dashboard/testimonial_form.html"
    fields = ["name", "message", "avatar"]
    success_url = "/dashboard/testimonials/"

    def form_valid(self, form):
        messages.success(self.request, "Testimonial created successfully")
        return super().form_valid(form)


@method_decorator(staff_member, name="dispatch")
class TestimonialUpdate(DashboardMixin, UpdateView):
    model = Testimonial
    template_name = "dashboard/testimonial_form.html"
    fields = ["name", "message", "avatar"]
    success_url = "/dashboard/testimonials/"

    def form_valid(self, form):
        messages.success(self.request, "Testimonial updated successfully")
        return super().form_valid(form)


@require_POST
@staff_member
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.delete()
    messages.success(request, "Testimonial deleted successfully")
    return redirect("dashboard:testimonial_list")


# ──────────────────────────────────────────────
# CONTACT MESSAGES
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class ContactList(DashboardMixin, ListView):
    model = ContactMessage
    template_name = "dashboard/contact_list.html"
    context_object_name = "contacts"
    paginate_by = 25
    queryset = ContactMessage.objects.order_by("-created_at")


@require_POST
@staff_member
def contact_delete(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    contact.delete()
    messages.success(request, "Contact message deleted successfully")
    return redirect("dashboard:contact_list")


# ──────────────────────────────────────────────
# NEWSLETTER SUBSCRIBERS
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class NewsletterList(DashboardMixin, ListView):
    model = NewsletterSubscription
    template_name = "dashboard/newsletter_list.html"
    context_object_name = "subscribers"
    paginate_by = 25
    queryset = NewsletterSubscription.objects.order_by("-created_at")


@require_POST
@staff_member
def newsletter_delete(request, pk):
    sub = get_object_or_404(NewsletterSubscription, pk=pk)
    sub.delete()
    messages.success(request, "Subscriber deleted successfully")
    return redirect("dashboard:newsletter_list")


# ──────────────────────────────────────────────
# SITE CONFIG
# ──────────────────────────────────────────────

@staff_member
def site_config_edit(request):
    config = SiteConfig.objects.first()
    if not config:
        config = SiteConfig.objects.create()

    if request.method == "POST":
        config.whatsapp_number = request.POST.get("whatsapp_number", "")
        config.phone_number = request.POST.get("phone_number", "")
        config.support_email = request.POST.get("support_email", "")
        config.site_name = request.POST.get("site_name", "Rian Audio Sounds")
        config.save()
        messages.success(request, "Site configuration updated successfully")
        return redirect("dashboard:site_config")

    return render(request, "dashboard/site_config_form.html", {"config": config})


# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────

@method_decorator(staff_member, name="dispatch")
class UserList(DashboardMixin, ListView):
    model = User
    template_name = "dashboard/user_list.html"
    context_object_name = "users"
    paginate_by = 25
    queryset = User.objects.order_by("-date_joined")
