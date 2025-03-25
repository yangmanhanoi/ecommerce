from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Shipping
from .serializers import ShippingSerializer
from datetime import datetime
import requests
from django.conf import settings

PAYMENT_SERVICE_URL = 'http://localhost:8001/api/payments/'

# API 1: Create a Shipment (Called after checkout)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_shipment(request):
    """Create shipment after checkout"""
  
    cart_id = request.data.get('cart_id')  # Get cart ID from request
    items = request.data.get('items', [])  # Get items from request

    if not cart_id or not items:
        return Response({"error": "Cart ID and items are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Generate a tracking number (this should ideally be more robust)
    tracking_number = f"TRK{cart_id}{datetime.utcnow().timestamp()}"

    shipment = Shipping.objects.create(
        cart_id=cart_id,
        tracking_number=tracking_number,
        carrier="Shopee",  # Default carrier
        shipping_address=request.data.get("shipping_address", ""),
        shipping_cost=request.data.get("shipping_cost", 0.00),
        status="pending"
    )

    serializer = ShippingSerializer(shipment)

    # Notify Payment Service
    # payment_payload = {
    #     "user_id": user_id,
    #     "shipment_id": shipment.id,
    #     "amount": shipment.shipping_cost,
    #     "tracking_number": tracking_number
    # }
    
    # payment_response = requests.post(f"{PAYMENT_SERVICE_URL}/create-payment", json=payment_payload, headers={"Authorization": request.headers.get("Authorization")})

    # if payment_response.status_code != 201:
    #     return Response({"error": "Failed to initiate payment", "details": payment_response.json()}, status=payment_response.status_code)

    # return Response({"shipment": serializer.data, "payment": payment_response.json()}, status=status.HTTP_201_CREATED)
    return Response({"shipment": serializer.data}, status=status.HTTP_201_CREATED)


# API 2: Get a specific shipment (Admin)
@api_view(['GET'])
# @permission_classes([IsAdminUser])
def get_shipment(request, shipment_id):
    try:
        shipment = Shipping.objects.get(id=shipment_id)
        serializer = ShippingSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Shipping.DoesNotExist:
        return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)


# API 3: Get all shipments for a customer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_customer_shipments(request):
    user_id = request.user.id
    status_param = request.query_params.get('status', None)

    shipments = Shipping.objects.filter(cart_id=user_id)  # Assuming cart_id represents user_id
    if status_param:
        shipments = shipments.filter(status=status_param)

    serializer = ShippingSerializer(shipments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# API 4: Track a shipment by tracking number
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def track_shipment(request, identifier):
    """
    Retrieve shipment details using either tracking_number or shipment_id.
    """
    try:
        if identifier.isdigit():  # If identifier is all digits, assume it's a shipment_id
            shipment = Shipping.objects.get(id=identifier)
        else:  # Otherwise, assume it's a tracking_number
            shipment = Shipping.objects.get(tracking_number=identifier)

        serializer = ShippingSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Shipping.DoesNotExist:
        return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)



# API 5: Update shipment status (Admin only)
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_shipment_status(request, shipment_id):
    try:
        shipment = Shipping.objects.get(id=shipment_id)
    except Shipping.DoesNotExist:
        return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status', None)
    if not new_status:
        return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

    shipment.status = new_status
    if new_status == "in_transit":
        shipment.estimated_delivery = datetime.utcnow().date()
    elif new_status == "delivered":
        shipment.actual_delivery = datetime.utcnow().date()

    shipment.save()

    return Response({"message": f"Shipment status updated to {new_status}"}, status=status.HTTP_200_OK)
