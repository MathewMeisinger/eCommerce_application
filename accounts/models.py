from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Adds a role field to distinguish vendors from buyers.
    """
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor')
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    @property
    def is_vendor(self):
        """Return True when the user is registered as a vendor."""
        return self.role == 'vendor'

    @property
    def is_buyer(self):
        """Return True when the user is registered as a buyer."""
        return self.role == 'buyer'


class VendorProfile(models.Model):
    """
    Store additional profile information for vendor users.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)

    def __str__(self):
        return self.store_name


class CustomerProfile(models.Model):
    """
    Store additional profile information for buyer users.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    email_address = models.EmailField()

    def __str__(self):
        return self.user.username
