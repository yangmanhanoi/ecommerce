from django.urls import path
from .views import LoginView, ProtectedView, SignupView

urlpatterns = [
    path('/login', LoginView.as_view(), name="login"),
    path('/protected', ProtectedView.as_view(), name='protected'),
    path('/signup', SignupView.as_view(), name='signup'),
]
