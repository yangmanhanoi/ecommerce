from django.urls import path
from .views import UserProfileView, UserProfileUpdateView, AddressListCreateView, AddressDetailView
urlpatterns = [
    path('/profile', UserProfileView.as_view(), name='profile'),
    path('/profile/update', UserProfileUpdateView.as_view(), name='update-view'),
    path('/address/create', AddressListCreateView.as_view(), name='address-list-create'),
    path('/address/<int:pk>', AddressDetailView.as_view(), name='address-detail')
]
