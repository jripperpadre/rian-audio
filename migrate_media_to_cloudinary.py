import os
import django
import cloudinary.uploader

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rian_backend.settings")
django.setup()

from shop.models import Product, ProductImage  # adjust if your models differ


def migrate_product_images():
    migrated = 0
    deleted = 0

    # ✅ Handle Product.main_image
    for product in Product.objects.all():
        if product.main_image and not str(product.main_image.url).startswith("http"):
            local_path = product.main_image.path
            if os.path.exists(local_path):
                print(f"Uploading {local_path}...")
                result = cloudinary.uploader.upload(local_path, folder="products")
                product.main_image = result["secure_url"]
                product.save(update_fields=["main_image"])
                migrated += 1

                # Delete old file
                try:
                    os.remove(local_path)
                    deleted += 1
                    print(f"🗑️ Deleted {local_path}")
                except Exception as e:
                    print(f"⚠️ Could not delete {local_path}: {e}")

    # ✅ Handle ProductImage (gallery)
    for img in ProductImage.objects.all():
        if img.image and not str(img.image.url).startswith("http"):
            local_path = img.image.path
            if os.path.exists(local_path):
                print(f"Uploading {local_path}...")
                result = cloudinary.uploader.upload(local_path, folder="products/gallery")
                img.image = result["secure_url"]
                img.save(update_fields=["image"])
                migrated += 1

                # Delete old file
                try:
                    os.remove(local_path)
                    deleted += 1
                    print(f"🗑️ Deleted {local_path}")
                except Exception as e:
                    print(f"⚠️ Could not delete {local_path}: {e}")

    print(f"✅ Done. Migrated {migrated} images to Cloudinary. Deleted {deleted} local files.")


if __name__ == "__main__":
    migrate_product_images()
