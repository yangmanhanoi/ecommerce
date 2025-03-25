from django.urls import path
from .views import create_shipment,get_shipment, get_all_customer_shipments, track_shipment, update_shipment_status

urlpatterns = [
    path('/create/', create_shipment, name='create_shipment'),
    path('/admin/<int:shipment_id>/', get_shipment, name='get_shipment'),
    path('/customer/', get_all_customer_shipments, name='get_all_customer_shipments'),
    path('/track/<str:identifier>/', track_shipment, name='track_shipment'),
    path('/<int:shipment_id>/status/', update_shipment_status, name='update_shipment_status'),
]
