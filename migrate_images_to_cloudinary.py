import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rian_backend.settings")
django.setup()

from cloudinary.uploader import upload
from shop.models import Product, Category, ProductImage, Testimonial


def migrate_field(obj, field_name):
    field = getattr(obj, field_name)
    if field and not str(field).startswith("http"):
        try:
            print(f"➡ Uploading {field} for {obj}")
            result = upload(field.path, folder=field.field.upload_to)
            setattr(obj, field_name, result["secure_url"])
            obj.save(update_fields=[field_name])
        except Exception as e:
            print(f"❌ Failed for {obj}: {e}")


for model, field in [
    (Product, "main_image"),
    (Category, "image"),
    (ProductImage, "image"),
    (Testimonial, "avatar"),
]:
    for obj in model.objects.all():
        migrate_field(obj, field)

print("✅ Migration finished")
