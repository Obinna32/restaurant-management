from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    CHEF = "CHEF", "Chef"
    WAITER = 'WAITER', "Waiter"
    CUSTOMER = "CUSTOMER", 'Customer'

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER,)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"