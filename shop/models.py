from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Testimonial(TimeStamped):
    name = models.CharField(max_length=100)
    message = models.TextField()
    avatar = models.ImageField(upload_to="testimonials/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.message[:30]}"

class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)  # 🔒 enforce unique emails
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(TimeStamped):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Category(TimeStamped):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Product(TimeStamped):
    BADGE_CHOICES = [
        ("", "None"),
        ("new", "New"),
        ("sale", "Sale"),
        ("best", "Best Seller"),
    ]

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()  # KES
    old_price = models.PositiveIntegerField(null=True, blank=True)  # for discounts
    watts = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="products"
    )

    # ✅ Main image (required in form, optional in DB for safety)
    main_image = models.ImageField(
        upload_to="products/main/",
        blank=False,
        null=True,
        help_text="Main product image (shown as thumbnail and hero)"
    )

    featured = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    badge_type = models.CharField(
        max_length=20,
        choices=BADGE_CHOICES,
        blank=True,
        default=""
    )
    whatsapp_number = models.CharField(
        max_length=32,
        blank=True,
        help_text="Optional per-product WhatsApp contact"
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    # ---------- Helper properties ----------
    @property
    def is_new(self):
        return self.badge_type == "new"

    @property
    def on_sale(self):
        return self.badge_type == "sale" or (
            self.old_price and self.old_price > self.price
        )

    @property
    def is_best_seller(self):
        return self.badge_type == "best"

    @property
    def display_whatsapp(self):
        """Returns product's WhatsApp number, falling back to global SiteConfig."""
        if self.whatsapp_number:
            return self.whatsapp_number
        cfg = SiteConfig.objects.first()
        return cfg.whatsapp_number if cfg else "+254700000000"


class ProductImage(TimeStamped):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(
        upload_to="products/gallery/",
        help_text="Additional gallery image"
    )

    def __str__(self):
        return f"Image for {self.product.name}"



class Review(TimeStamped):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    text = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class Address(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=140)
    phone = models.CharField(max_length=32)
    line1 = models.CharField(max_length=160)
    line2 = models.CharField(max_length=160, blank=True)
    city = models.CharField(max_length=80)
    notes = models.CharField(max_length=200, blank=True)


class Order(TimeStamped):
    STATUS_CHOICES = [
        ("new", "New"),
        ("processing", "Processing"),
        ("sent", "Sent"),
        ("done", "Done"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    whatsapp_number = models.CharField(max_length=32, blank=True)  # for customer notification

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.status}"

    def recalc_total(self):
        self.total = sum(item.qty * item.price_each for item in self.items.all())
        self.save(update_fields=["total"])


class OrderItem(TimeStamped):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    price_each = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.qty} x {self.product.name}"

    @property
    def subtotal(self):
        return self.qty * self.price_each


class SiteConfig(models.Model):
    """Global settings like WhatsApp, phone, and email support"""

    site_name = models.CharField(max_length=100, default="Rian Audio Sounds")

    # Contact channels
    whatsapp_number = models.CharField(
        max_length=32,
        default="+254700000000",
        help_text="Enter in international format e.g. +254700000000"
    )
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="Main call number e.g. +254700000000"
    )
    support_email = models.EmailField(
        default="support@example.com",
        help_text="Support contact email"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return f"{self.username} ({self.email})"

    # ✅ Add these
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.username
