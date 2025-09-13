import os
from django.core.management.base import BaseCommand
from django.conf import settings
from shop.models import Category, Product, ProductImage, Testimonial
import cloudinary.uploader

class Command(BaseCommand):
    help = "Upload existing media files to Cloudinary"

    def handle(self, *args, **options):
        models_to_check = [
            (Category, "image"),
            (Product, "main_image"),
            (ProductImage, "image"),
            (Testimonial, "avatar"),
        ]

        for model, field in models_to_check:
            self.stdout.write(self.style.NOTICE(f"Processing {model.__name__}..."))
            for obj in model.objects.all():
                image_field = getattr(obj, field)
                if image_field and os.path.exists(image_field.path):
                    self.stdout.write(f"  Uploading {image_field.path}...")
                    try:
                        result = cloudinary.uploader.upload(
                            image_field.path,
                            folder=image_field.field.upload_to,
                        )
                        image_field.name = result["public_id"] + "." + result["format"]
                        obj.save(update_fields=[field])
                        self.stdout.write(self.style.SUCCESS(f"  ✅ Uploaded {image_field.name}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ❌ Error: {e}"))
