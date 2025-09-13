# migrate_media_to_cloudinary.py
import os
import django
from django.core.files import File
from django.core.files.storage import default_storage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rian_backend.settings")
django.setup()

from shop.models import Product, Category, Testimonial, SiteConfig

def migrate_queryset(model, field_name):
    print(f"Processing {model.__name__}...")
    updated = 0
    for obj in model.objects.all():
        image_field = getattr(obj, field_name)
        if not image_field:
            continue

        # If already Cloudinary (res.cloudinary.com), skip
        if str(image_field).startswith("http") and "cloudinary" in str(image_field):
            continue

        try:
            print(f" - Migrating {obj} ({image_field})")
            with open(image_field.path, "rb") as f:
                image_field.save(os.path.basename(image_field.name), File(f), save=True)
            updated += 1
        except Exception as e:
            print(f"   !! Failed for {obj}: {e}")
    print(f"✔ {updated} {model.__name__} images migrated.\n")


def run():
    migrate_queryset(Category, "image")
    migrate_queryset(Product, "image")
    migrate_queryset(Testimonial, "photo")   # adjust if field is different
    migrate_queryset(SiteConfig, "logo")     # adjust if field is different
    print("🎉 Migration finished.")


if __name__ == "__main__":
    run()
