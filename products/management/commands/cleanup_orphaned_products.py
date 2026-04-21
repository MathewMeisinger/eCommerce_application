from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = "Soft-delete orphaned products"

    def handle(self, *args, **options):
        qs = Product.objects.filter(store__isnull=True, is_active=True)
        count = qs.update(is_active=False)
        self.stdout.write(self.style.SUCCESS(
            f"{count} orphaned products soft-deleted"
        ))
