import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from openpyxl import Workbook
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

from .models import (
    Category, Product, ProductImage, Review,
    Order, OrderItem, Address,
    NewsletterSubscription, ContactMessage, Testimonial,
    SiteConfig
)

# -----------------------
# Export Utilities
# -----------------------

def export_as_csv_action(description="Export selected objects as CSV",
                         fields=None, exclude=None, header=True):
    """Reusable admin action to export objects as CSV."""
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]

        if fields:
            field_names = fields
        if exclude:
            field_names = [f for f in field_names if f not in exclude]

        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = (
            f'attachment; filename={opts.verbose_name_plural}_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
        )
        writer = csv.writer(response)

        if header:
            writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = description
    return export_as_csv


def export_as_excel_action(description="Export selected objects as Excel",
                           fields=None, exclude=None, header=True):
    """Reusable admin action to export objects as Excel (.xlsx)."""
    def export_as_excel(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]

        if fields:
            field_names = fields
        if exclude:
            field_names = [f for f in field_names if f not in exclude]

        wb = Workbook()
        ws = wb.active
        ws.title = opts.verbose_name_plural.capitalize()

        if header:
            ws.append(field_names)

        for obj in queryset:
            ws.append([getattr(obj, field) for field in field_names])

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = (
            f'attachment; filename={opts.verbose_name_plural}_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx'
        )
        wb.save(response)
        return response
    export_as_excel.short_description = description
    return export_as_excel


# -----------------------
# Admin Registrations
# -----------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "image", "slug", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    date_hierarchy = "created_at"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ["preview"]

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" style="border-radius:4px; object-fit:cover;" />',
                obj.image.url
            )
        return "-"
    preview.short_description = "Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = (
        "thumbnail", "name", "category", "price_display", "watts",
        "stock", "badge_colored", "featured", "created_at"
    )
    list_filter = ("featured", "category", "badge_type", "created_at")
    search_fields = ("name", "description")
    inlines = [ProductImageInline]
    ordering = ("-created_at",)
    list_editable = ("featured", "stock")
    date_hierarchy = "created_at"

    fieldsets = (
        ("Basic Info", {"fields": (
            "name", "slug", "category", "description", "main_image",
            "featured", "badge_type"
        )}),
        ("Pricing & Stock", {"fields": ("price", "old_price", "stock", "watts")}),
        ("Contact", {"fields": ("whatsapp_number",)}),
    )

    actions = [
        export_as_csv_action("Export selected products to CSV"),
        export_as_excel_action("Export selected products to Excel"),
    ]

    def thumbnail(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="60" style="border-radius:4px; object-fit:cover;" />', obj.main_image.url)
        return "-"
    thumbnail.short_description = "Main Image"

    def price_display(self, obj):
        if obj.old_price and obj.old_price > obj.price:
            return format_html(
                '<span style="color:green; font-weight:600;">KES {}</span> '
                '<span style="text-decoration:line-through; color:gray;">KES {}</span>',
                obj.price, obj.old_price
            )
        return f"KES {obj.price}"
    price_display.short_description = "Price"

    def badge_colored(self, obj):
        colors = {"new": "blue", "sale": "red", "best": "green"}
        if obj.badge_type:
            color = colors.get(obj.badge_type, "black")
            return format_html('<span style="color:{}; font-weight:600;">{}</span>', color, obj.get_badge_type_display())
        return "-"
    badge_colored.short_description = "Badge"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    search_fields = ("product__name", "user__username", "text")
    list_filter = ("rating", "created_at")
    date_hierarchy = "created_at"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "colored_status", "total", "customer_whatsapp_link", "admin_whatsapp_link", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "whatsapp_number", "address__full_name")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)
    list_editable = ("total",)
    readonly_fields = ("total",)
    date_hierarchy = "created_at"

    actions = [
        "mark_processing", "mark_sent", "mark_done",
        export_as_csv_action("Export selected orders to CSV",
                             fields=["id", "user", "status", "total", "created_at"]),
        export_as_excel_action("Export selected orders to Excel",
                               fields=["id", "user", "status", "total", "created_at"]),
    ]

    def mark_processing(self, request, queryset):
        updated = queryset.update(status="processing")
        self.message_user(request, f"{updated} orders marked as Processing.")

    def mark_sent(self, request, queryset):
        updated = queryset.update(status="sent")
        self.message_user(request, f"{updated} orders marked as Sent.")

    def mark_done(self, request, queryset):
        updated = queryset.update(status="done")
        self.message_user(request, f"{updated} orders marked as Done.")

    mark_processing.short_description = "Mark selected orders as Processing"
    mark_sent.short_description = "Mark selected orders as Sent"
    mark_done.short_description = "Mark selected orders as Done"

    def colored_status(self, obj):
        colors = {"new": "gray", "processing": "orange", "sent": "blue", "done": "green"}
        return mark_safe(f'<b style="color:{colors.get(obj.status, "black")}">{obj.get_status_display()}</b>')
    colored_status.short_description = "Status"

    def customer_whatsapp_link(self, obj):
        if obj.address and obj.address.phone:
            return format_html('<a href="https://wa.me/{}" target="_blank">Chat Customer</a>', obj.address.phone)
        return "-"
    customer_whatsapp_link.short_description = "Customer WhatsApp"

    def admin_whatsapp_link(self, obj):
        if obj.whatsapp_number:
            return format_html('<a href="https://wa.me/{}" target="_blank">Chat Admin</a>', obj.whatsapp_number)
        return "-"
    admin_whatsapp_link.short_description = "Admin WhatsApp"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.recalc_total()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalc_total()


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "city", "created_at")
    search_fields = ("user__username", "full_name", "phone", "city")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    actions = [
        export_as_csv_action("Export selected customers to CSV",
                             fields=["id", "user", "full_name", "phone", "city", "line1", "line2", "notes"]),
        export_as_excel_action("Export selected customers to Excel",
                               fields=["id", "user", "full_name", "phone", "city", "line1", "line2", "notes"]),
    ]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "message")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
    search_fields = ("email",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    actions = [
        export_as_csv_action("Export selected subscriptions to CSV",
                             fields=["id", "email", "created_at"]),
        export_as_excel_action("Export selected subscriptions to Excel",
                               fields=["id", "email", "created_at"]),
        "remove_duplicates",
    ]

    def remove_duplicates(self, request, queryset):
        """Remove duplicate emails, keep the earliest subscription."""
        seen = set()
        duplicates = []
        for sub in NewsletterSubscription.objects.order_by("email", "created_at"):
            if sub.email in seen:
                duplicates.append(sub.id)
            else:
                seen.add(sub.email)

        deleted, _ = NewsletterSubscription.objects.filter(id__in=duplicates).delete()
        self.message_user(request, f"Removed {deleted} duplicate subscription(s).")

    remove_duplicates.short_description = "Remove duplicate subscriptions"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    search_fields = ("name", "email", "subject", "message")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("whatsapp_number", "support_email")
    search_fields = ("whatsapp_number", "support_email")

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists() and super().has_add_permission(request)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "username", "password1", "password2", "is_staff", "is_active")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
