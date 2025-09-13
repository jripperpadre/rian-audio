import os
from django.core.management.base import BaseCommand
from shop.models import Category, Product, ProductImage, Testimonial
import cloudinary.uploader


class Command(BaseCommand):
    help = "Upload existing local media files to Cloudinary, update DB, and remove local copies"

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

                # Skip if no image
                if not image_field:
                    continue

                # Skip if already Cloudinary URL
                if str(image_field).startswith("http"):
                    continue

                # Local file path
                local_path = getattr(image_field, "path", None)
                if not local_path or not os.path.exists(local_path):
                    continue

                self.stdout.write(f"  Uploading {local_path}...")

                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder=image_field.field.upload_to or model.__name__.lower(),
                    )

                    # Save Cloudinary secure URL
                    image_field.name = result["secure_url"]
                    obj.save(update_fields=[field])

                    # Delete local file
                    os.remove(local_path)

                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ Uploaded & deleted {local_path}")
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Error: {e}"))
