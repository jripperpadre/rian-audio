from django.core.management.base import BaseCommand
from shop.models import Product, Category, ProductImage
from cloudinary.uploader import upload


class Command(BaseCommand):
    help = "Fix all image fields (Product.main_image, Category.image, ProductImage.image) by uploading local/static images to Cloudinary."

    def handle(self, *args, **options):
        total_updated = 0
        total_skipped = 0

        # ---------- Product.main_image ----------
        updated, skipped = self.fix_images(Product, "main_image")
        self.stdout.write(self.style.SUCCESS(
            f"Products → Updated {updated}, Skipped {skipped}"
        ))
        total_updated += updated
        total_skipped += skipped

        # ---------- Category.image ----------
        updated, skipped = self.fix_images(Category, "image")
        self.stdout.write(self.style.SUCCESS(
            f"Categories → Updated {updated}, Skipped {skipped}"
        ))
        total_updated += updated
        total_skipped += skipped

        # ---------- ProductImage.image ----------
        updated, skipped = self.fix_images(ProductImage, "image")
        self.stdout.write(self.style.SUCCESS(
            f"ProductImages → Updated {updated}, Skipped {skipped}"
        ))
        total_updated += updated
        total_skipped += skipped

        # ---------- Summary ----------
        self.stdout.write(self.style.SUCCESS(
            f"✅ Done! Total Updated: {total_updated}, Total Skipped: {total_skipped}"
        ))

    def fix_images(self, model, field_name):
        updated = 0
        skipped = 0

        for obj in model.objects.all():
            field_value = getattr(obj, field_name)

            if not field_value:
                skipped += 1
                continue

            if "res.cloudinary.com" in str(field_value):
                skipped += 1
                continue

            try:
                result = upload(str(field_value))
                setattr(obj, field_name, result["secure_url"])
                obj.save(update_fields=[field_name])
                updated += 1

                self.stdout.write(self.style.SUCCESS(
                    f"✔ Updated {model.__name__} {obj.id} ({obj})"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"⚠ Error updating {model.__name__} {obj.id} ({obj}): {e}"
                ))
                skipped += 1

        return updated, skipped
