from django.db import models
from django.conf import settings


class Cart(models.Model):
    """
    Represent the current shopping cart for a buyer.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        """Return the combined total for all items in the cart."""
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    """
    Represent a single product entry inside a cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    # Use a string reference here to avoid circular imports.
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def total_price(self):
        """Return the subtotal for this cart line."""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} - {self.product.name}"


class Order(models.Model):
    """
    Represent a completed checkout by a buyer.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username} ({self.created_at.date()})"


class OrderItem(models.Model):
    """
    Represent a single purchased item within an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    # Use a string reference again to avoid circular imports.
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    price_each = models.DecimalField(max_digits=12, decimal_places=2,
                                     default=0)

    def __str__(self):
        return f"{self.quantity} × {self.product.name} @ {self.price_each}"
