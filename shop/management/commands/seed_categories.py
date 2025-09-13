from django.core.management.base import BaseCommand
from shop.models import Category

class Command(BaseCommand):
    help = "Seeds default categories into the database."

    def handle(self, *args, **kwargs):
        categories = [
            "Hometheatre systems",
            "Bass speakers",
            "Amplifiers",
            "Home appliances",
            "Kitchen appliances",
            "Sound systems",
            "Car systems",
            "Equalizers",
        ]

        for name in categories:
            obj, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created category: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Already exists: {name}"))

        self.stdout.write(self.style.SUCCESS("🎉 Category seeding complete!"))
