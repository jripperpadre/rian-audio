from .models import Category, SiteConfig
from .cart import Cart
def categories_processor(request):
    """Make all categories globally available (e.g. navbar, footer)."""
    return {
        "categories": Category.objects.all()
    }

def site_config(request):
    """Make SiteConfig globally available (e.g. WhatsApp number, logo, etc.)."""
    return {
        "site_config": SiteConfig.objects.first()
    }


def cart_context(request):
    """Add cart to context so it's available everywhere."""
    return {
        "cart": Cart(request)
    }
