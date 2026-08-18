from django.db import models
from django.conf import settings

# Create your models here.
class Table(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['table_number']

    def __str__(self):
        return f"Table {self.table_number} (Capacity: {self.capacity})"
    

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PENDING', 'Pending'),
        ('PENDING', 'Pending'),
        ('PENDING', 'Pending'),
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'reservations')
    guest_count = models.PositiveIntegerField(default=1)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


    class Meta:
        ordering = ['-reservation_date', '-reservation_time']

    def __str__(self):
        return f"Reservation {self.id} - {self.customer.username} ({self.reservation_date} {self.reservation_time})"