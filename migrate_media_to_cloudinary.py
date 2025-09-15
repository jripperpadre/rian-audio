import os
import django
import cloudinary.uploader

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rian_backend.settings")
django.setup()

from shop.models import Testimonial, Category, Product, ProductImage


def upload_and_replace(instance, field_name, folder):
    file_field = getattr(instance, field_name)
    if not file_field:
        return False, False

    try:
        local_path = file_field.path  # only exists if file is local
    except NotImplementedError:
        return False, False

    if os.path.exists(local_path):
        print(f"Uploading {local_path} → Cloudinary/{folder}")
        result = cloudinary.uploader.upload(local_path, folder=folder)
        # Store Cloudinary reference (public_id.format) so Django storage works
        file_field.name = result["public_id"] + "." + result["format"]
        instance.save(update_fields=[field_name])

        try:
            os.remove(local_path)
            print(f"🗑️ Deleted {local_path}")
            return True, True
        except Exception as e:
            print(f"⚠️ Could not delete {local_path}: {e}")
            return True, False
    return False, False


def migrate():
    migrated = deleted = 0

    for t in Testimonial.objects.all():
        m, d = upload_and_replace(t, "avatar", "testimonials")
        migrated += m
        deleted += d

    for c in Category.objects.all():
        m, d = upload_and_replace(c, "image", "categories")
        migrated += m
        deleted += d

    for p in Product.objects.all():
        m, d = upload_and_replace(p, "main_image", "products/main")
        migrated += m
        deleted += d

    for img in ProductImage.objects.all():
        m, d = upload_and_replace(img, "image", "products/gallery")
        migrated += m
        deleted += d

    print(f"✅ Done. Migrated {migrated} images, deleted {deleted} local files.")


if __name__ == "__main__":
    migrate()
