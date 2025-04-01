from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import UserProfile
from .models import Address
from api.models import CustomerType

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    customer_type = serializers.ChoiceField(choices=CustomerType.choices, required=False)  # ✅ Add this line

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'phoneNumber', 'imageUrl', 'customer_type']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phoneNumber = serializers.CharField(required=False)
    imageUrl = serializers.URLField(required=False)

    class Meta:
        model = UserProfile
        fields = ["username", "email", "phoneNumber", "imageUrl"]

    def update(self, instance, validated_data):
        # Update UserProfile fields
        instance.phoneNumber = validated_data.get("phoneNumber", instance.phoneNumber)
        instance.imageUrl = validated_data.get("imageUrl", instance.imageUrl)
        instance.save()
        return instance

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'country', 'postal_code', 'phone_number', 'is_default']

    def validate_is_default(self, value):
        """Ensure only one address is set as default per user."""
        user = self.context['request'].user
        if value and Address.objects.filter(user=user, is_default=True).exists():
            raise serializers.ValidationError("You can only have one default address.")
        return value