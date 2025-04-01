from rest_framework import serializers
from .models import UserProfile, CustomerType
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class SignupSerializer(serializers.ModelSerializer):
    phoneNumber = serializers.CharField(max_length=15, required=True)
    imageUrl = serializers.URLField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phoneNumber', 'imageUrl']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone_number = validated_data.pop('phoneNumber')
        image_url = validated_data.pop('imageUrl', None)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        # Create UserProfile with additional fields
        UserProfile.objects.create(user=user, phoneNumber=phone_number, imageUrl=image_url)
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Get the user profile details
        try:
            profile = UserProfile.objects.get(user = user)
            phone_number = profile.phoneNumber
            image_url = profile.imageUrl
        except UserProfile.DoesNotExist:
            phone_number = None
            image_url = None
        

        if user.is_superuser:
            role = 'admin'
        else:
            role = user.groups.first().name if user.groups.exists() else "user"  # Assuming role is stored in Groups
        #Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['phoneNumber'] = phone_number
        token['imageUrl'] = image_url
        token['role'] = role

        return token
    
class UserProfileSerializer(serializers.ModelSerializer):
    customer_type = serializers.ChoiceField(choices=CustomerType.choices, required=True)

    class Meta:
        model = UserProfile
        fields = ['customer_type']