from django.db import models

class Shipping(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    cart_id = models.UUIDField()  # Store Cart ID as UUID (assuming Cart uses UUIDs)
    tracking_number = models.CharField(max_length=50, unique=True, db_index=True)
    carrier = models.CharField(max_length=100)
    shipping_address = models.TextField()
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipping'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['cart_id']),
        ]

    def __str__(self):
        return f"Shipping {self.tracking_number} - {self.carrier} - {self.status}"
