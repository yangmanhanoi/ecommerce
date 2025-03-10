from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNumber = models.CharField(max_length=15, unique=True)
    imageUrl = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username
# Create your models here.
