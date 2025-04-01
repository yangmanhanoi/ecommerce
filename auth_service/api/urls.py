from django.urls import path
from .views import *

urlpatterns = [
    path('/login', LoginView.as_view(), name="login"),
    path('/protected', ProtectedView.as_view(), name='protected'),
    path('/signup', SignupView.as_view(), name='signup'),
    path('/users/<int:user_id>/customer-type', AssignCustomerTypeView.as_view(), name='assign-customer-type'),
    path('/users/customer-types/', GetCustomerTypeView.as_view(), name='get-customer-types'),
    path('/users/<int:user_id>/customer-type/remove/', RemoveCustomerTypeView.as_view(), name='remove-customer-type'),
]
