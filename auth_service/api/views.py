from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, views, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import SignupSerializer, CustomTokenObtainPairSerializer

# Create your views here.
class SignupView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request,username=username,password=password)

        if user is not None:
            serializer = CustomTokenObtainPairSerializer()
            refresh = serializer.get_token(user=user)

            # refresh = RefreshToken.for_user(user=user)
            user_type = "admin" if user.is_superuser else "user"
            return Response({
                "user_type": user_type,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
class ProtectedView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello, {request.user.username}!"})