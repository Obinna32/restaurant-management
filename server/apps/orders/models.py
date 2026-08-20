from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.menu.models import MenuItem
from apps.reservations.models import Table

# Create your models here.
class Order(models.Model):
    ORDER_TYPE_CHOICES = (
        ('DINE_IN', 'Dine In'),
        ('TAKEAWAY', 'Takeaway'),
        ('DELIVERY', 'Delivery'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('SERVED', 'Served'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_type = models.CharField(max_length=20, choices = ORDER_TYPE_CHOICES, default='DINE_IN')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default= Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def calculate_total(self):
        total = sum(item.get_cost() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def __str__(self):
        return f"Order #{self.id} - {self.order_type} ({self.status})"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item= models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name = 'order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.CharField(max_length=255,blank=True, null=True)

    def get_cost(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.unit_price and self.menu_item:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} (Order #{self.order.id})"
    
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('ONLINE', 'Online'),
    )
    STATUS_CHHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )

    order = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CARD')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"