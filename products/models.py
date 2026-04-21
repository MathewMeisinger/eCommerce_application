from django.db import models
from stores.models import Store
from accounts.models import User
from django.conf import settings
from django.apps import apps


class Product(models.Model):
    """
    Represent a product sold by a store on the platform.
    """
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
        )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class Review(models.Model):
    """
    Represent a review left by a user on a product.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
        )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Mark reviews as verified only when the user has purchased the product.
        OrderItem = apps.get_model('orders', 'OrderItem')
        bought = OrderItem.objects.filter(
            order__user=self.user,
            product=self.product
        ).exists()
        self.is_verified = bought
        super().save(*args, **kwargs)
