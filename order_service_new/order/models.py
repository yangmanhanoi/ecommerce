from django.db import models
from django.utils.timezone import now
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled')
    ]
    
    user_id = models.IntegerField()
    shipment_id = models.IntegerField()  # Reference to shipment service
    payment_id = models.IntegerField()  # Reference to payment service
    total_price = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=now)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.FloatField()