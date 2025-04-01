from django.db import models
from django.contrib.auth.models import User


class CustomerType(models.TextChoices):
    CASUAL_SHOPPER = "Casual Shopper", "Casual Shopper"
    DISCOUNT_HUNTER = "Discount Hunter", "Discount Hunter"
    ONE_TIME_BUYER = "One-Time Buyer", "One-Time Buyer"
    LOYAL_CUSTOMER = "Loyal Customer", "Loyal Customer"
    MOBILE_FIRST = "Mobile-First Shopper", "Mobile-First Shopper"
    SOCIAL_MEDIA_BUYER = "Social Media Buyer", "Social Media Buyer"
    SUBSCRIPTION_BASED = "Subscription-Based Customer", "Subscription-Based Customer"
    LAST_MINUTE_BUYER = "Last-Minute Buyer", "Last-Minute Buyer"
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNumber = models.CharField(max_length=15, unique=True)
    imageUrl = models.URLField(blank=True, null=True)
    customer_type = models.CharField(
        max_length=50, choices=CustomerType.choices, default=CustomerType.CASUAL_SHOPPER
    )

    def __str__(self):
        return self.user.username
# Create your models here.
