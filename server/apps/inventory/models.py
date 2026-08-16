from django.db import models
from django.conf import settings


# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=198)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='suppliers_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilogram'),
        ('g', "Grams"),
        ('L', 'Litres'),
        ('ml', 'Millilitres'),
        ('pcs', 'Pieces'),
        ('pack', 'Packs'),
    )
    name = models.CharField(max_length=150, unique=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_items')
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level
    
    class Meta: 
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
    

    