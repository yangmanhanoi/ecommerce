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
SHIPMENT_SERVICE_URL = 'http://localhost:5003/shipments/'

def get_product_detail(product_id):
    """Lấy thông tin sản phẩm từ Product Service"""
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        return None
    return None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Thêm sản phẩm vào giỏ hàng"""
    user_id = request.user.id
    data = request.data
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)

    product_detail = get_product_detail(product_id)
    if not product_detail:
        return Response({"error": "Product not found"}, status=404)

    price = product_detail.get("price", 0)

    cart, _ = Cart.objects.get_or_create(user_id=user_id)
    cart_item = CartItem.objects.create(cart=cart, product_id=product_id)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
    
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    
    cart_item.price_at_addition = price
    cart_item.price_at_addition = price
    cart_item.save()

    return Response({"message": "Product added to cart!", "cart_item_id": cart_item.id}, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, cart_item_id):
    """Xóa sản phẩm khỏi giỏ hàng"""
    user_id = request.user.id
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user_id=user_id)
    
    cart_item.delete()
    return Response({"message": "Item removed from cart"}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart_items(request):
    """Lấy danh sách sản phẩm trong giỏ hàng"""
    user_id = request.user.id
    cart = Cart.objects.filter(user_id=user_id).first()

    if not cart:
        return Response({"message": "Cart is empty"}, status=200)

    cart_items = cart.items.all()
    detailed_cart = []
    total_price = 0

    for item in cart_items:
        product_details = get_product_detail(item.product_id)
        if product_details:
            total_price += product_details.get("price", 0) * item.quantity
            detailed_cart.append({
                "cart_id": item.id,
                "product": product_details,
                "quantity": item.quantity,
                "added_at": item.added_at.strftime("%Y-%m-%d %H:%M:%S")
            })

    return Response({
        "user_id": user_id,
        "cart_items": detailed_cart,
        "total_price": total_price
    }, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_cart(request, cart_item_id):
    """Chỉnh sửa số lượng sản phẩm trong giỏ hàng"""
    user_id = request.user.id
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user_id=user_id)

    new_quantity = request.data.get("quantity")
    if new_quantity is None or new_quantity <= 0:
        return Response({"message": "Invalid quantity"}, status=400)
    
    cart_item.quantity = new_quantity
    cart_item.save()

    return Response({"message": "Cart item updated successfully"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_total_price(request):
    """Tính tổng giá trị giỏ hàng"""
    data = request.data
    if "items" not in data or not isinstance(data["items"], list):
        return Response({"error": "Invalid request body, must contain 'items' as a list"}, status=400)

    total_price = 0.0
    for item in data['items']:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)

        product_detail = get_product_detail(product_id)
        if product_detail:
            total_price += product_detail.get("price", 0) * quantity

    return Response({"total_price": total_price}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_cart_by_time(request):
    """Lọc giỏ hàng theo thời gian thêm sản phẩm"""
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")

    if not start_date or not end_date:
        return Response({"error": "Both start_date and end_date are required"}, status=400)

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

    cart_items = CartItem.objects.filter(added_at__range=[start_dt, end_dt])
    cart_data = [{"cart_id": item.id, "product_id": item.product_id, "quantity": item.quantity, "added_at": item.added_at} for item in cart_items]

    return Response(cart_data, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_out(request):
    """Xác nhận thanh toán & tạo đơn hàng"""
    data = request.data
    if "items" not in data or not isinstance(data["items"], list):
        return Response({"error": "Invalid request body, must contain 'items' as a list"}, status=400)

    headers = {"Authorization": request.headers.get('Authorization')}
    shipment_response = requests.post(f"{SHIPMENT_SERVICE_URL}create-shipment", json={"items": data['items']}, headers=headers)

    if shipment_response.status_code != 201:
        return Response({"error": "Failed to create order", "details": shipment_response.json()}, status=shipment_response.status_code)

    return Response(shipment_response.json(), status=201)
