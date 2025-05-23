from datetime import datetime
import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

PRODUCT_SERVICE_URL = 'http://localhost:5001/products/'
SHIPMENT_SERVICE_URL = 'http://localhost:5003/api/shipments/'

def get_product_detail(product_id):
    """Retrieve product details from Product Service"""
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

@api_view(['POST'])
# @csrf_exempt
# @token_required
# @permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add product to cart"""
    
    # user_id = request.user_data.get("user_id")
    serializer = CartItemSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_id = request.data.get("user_id")
    product_id = serializer.validated_data["product_id"]
    quantity = serializer.validated_data.get("quantity", 1)
    
    product_detail = get_product_detail(product_id)
    if not product_detail:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    product_price = product_detail.get("price")

    cart, _ = Cart.objects.get_or_create(user_id=user_id)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)

    if created:
        cart_item.quantity = quantity
        cart_item.price = product_price  # Store product price
    else:
        cart_item.quantity += quantity  # Increase quantity, price remains same

    cart_item.save()
    
    return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, cart_item_id):
    """Remove product from cart"""
    user_id = request.user.id
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user_id=user_id)
    cart_item.delete()
    return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_cart_items(request):
    """Retrieve cart items"""
    user_id = request.user.id
    # user_id = 1
    cart = Cart.objects.filter(user_id=user_id).first()
    if not cart:
        return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
    
    cart_items = cart.items.all()
    serialized_cart_items = CartItemSerializer(cart_items, many=True).data
    return Response({"user_id": user_id, "cart_items": serialized_cart_items}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_cart(request, cart_item_id):
    """Update cart item quantity"""
    user_id = request.user.id
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user_id=user_id)
    serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def calculate_total_price(request):
    """Calculate total cart price"""
    data = request.data.get("items", [])
    total_price = sum(
        get_product_detail(item["product_id"]).get("price", 0) * item.get("quantity", 1)
        for item in data if get_product_detail(item["product_id"])
    )
    return Response({"total_price": total_price}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_cart_by_time(request):
    """Filter cart items by added time"""
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    
    if not start_date or not end_date:
        return Response({"error": "Both start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    cart_items = CartItem.objects.filter(added_at__range=[start_dt, end_dt])
    return Response(CartItemSerializer(cart_items, many=True).data, status=status.HTTP_200_OK)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def check_out(request):
    user_id = request.data.get("user_id")
    # user_id = 1
    data = request.data.get("items", [])

    # Fetch the user's cart (assuming Cart is linked by user_id)
    cart = Cart.objects.filter(user_id=user_id).first()
    if not cart:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    headers = {"Authorization": request.headers.get("Authorization")}
    
    # Ensure cart_id is sent in the request
    shipment_payload = {
        "cart_id": cart.id,
        "items": data,
        "shipping_address": request.data.get("shipping_address", ""),  # Ensure required fields are included
        "shipping_cost": request.data.get("shipping_cost", 0.00)
    }

    shipment_response = requests.post(f"{SHIPMENT_SERVICE_URL}create/", json=shipment_payload, headers=headers)

    if shipment_response.status_code != 201:
        return Response({"error": "Failed to create shipment", "details": shipment_response.json()}, status=shipment_response.status_code)
    return Response(shipment_response.json(), status=status.HTTP_201_CREATED)