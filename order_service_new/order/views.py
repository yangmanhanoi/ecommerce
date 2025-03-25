from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from datetime import datetime
import requests

from .models import Order, OrderItem
from .serializers import OrderSerializer
# from .authentication import JWTAuthentication, token_required, admin_required

# Service URLs
CART_SERVICE_URL = 'http://localhost:8000/api/carts/'
SHIPMENT_SERVICE_URL = 'http://localhost:5003/api/shipments/'
PAYMENT_SERVICE_URL = 'http://localhost:8001/api/payments/'

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users access
    # authentication_classes = [JWTAuthentication]  # Uncomment if using JWT
    
    def get_queryset(self):
        """
        Return orders for authenticated user. Admins see all orders.
        """
        user = self.request.user
        if user.is_staff:  # Admins
            return Order.objects.all()
        return Order.objects.filter(user_id=user.id)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new order with items and include shipment cost.
        """
        user = request.user
        shipment_id = request.data.get('shipment_id')
        payment_id = request.data.get('payment_id')
        items = request.data.get('items', [])  # Expecting a list of items

        if not shipment_id or not payment_id:
            return Response({"error": "shipment_id and payment_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not items:
            return Response({"error": "Items list cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate items
        total_price = 0
        order_items = []
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            price = item.get('price')

            if not product_id or not quantity or not price:
                return Response({"error": "Each item must have product_id, quantity, and price"}, status=status.HTTP_400_BAD_REQUEST)

            total_price += quantity * price
            order_items.append(OrderItem(product_id=product_id, quantity=quantity, price=price))

        # Fetch shipment cost from Shipment Service
        shipping_cost = 0
        try:
            response = requests.get(f"{SHIPMENT_SERVICE_URL}track/{shipment_id}")
            response.raise_for_status()
            shipment_data = response.json()
            print(shipment_data)
            shipping_cost = shipment_data.get('shipping_cost', 0)  # Ensure there's a default value
        except requests.RequestException:
            return Response({"error": "Failed to fetch shipment cost"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        shipping_cost = float(shipping_cost)  # Convert to float if it's a string
        total_price += shipping_cost  # Add shipping cost to total price


        # Create order
        order = Order.objects.create(
            user_id=user.id,
            shipment_id=shipment_id,
            payment_id=payment_id,
            total_price=total_price
        )

        # Save order items
        for item in order_items:
            item.order = order
        OrderItem.objects.bulk_create(order_items)  # Efficient batch insert

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['put'])
    def cancel(self, request, pk=None):
        """
        Cancel an order and notify Cart Service to restore stock.
        Only pending orders can be canceled.
        """
        user = request.user
        order = self.get_object()

        if not user.is_staff and order.user_id != user.id:
            return Response({"error": "You don't have permission to cancel this order"}, status=status.HTTP_403_FORBIDDEN)

        if order.status != 'pending':
            return Response({"error": "Only pending orders can be canceled"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'canceled'
        order.save()

        # Notify Cart Service to restore stock
        try:
            response = requests.post(f"{CART_SERVICE_URL}restore_stock", json={"order_id": order.id})
            response.raise_for_status()  # Raise error if request fails
        except requests.RequestException as e:
            return Response({"error": "Failed to notify Cart Service", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Order canceled successfully", "order": OrderSerializer(order).data}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Admin-only: Update order status.
        """
        if not request.user.is_staff:
            return Response({"error": "Only admins can update order status"}, status=status.HTTP_403_FORBIDDEN)

        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status or new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        return Response({"message": "Order status updated successfully", "order": OrderSerializer(order).data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def user_orders(self, request):
        """
        Retrieve all orders for the authenticated user with optional filters.
        """
        queryset = self.get_queryset()

        status_filter = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if start_date and end_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                queryset = queryset.filter(created_at__range=(start_date_obj, end_date_obj))
            except ValueError:
                return Response({"error": "Invalid date format, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(queryset, many=True).data)

class PublicOrderView(APIView):
    """
    Public API endpoint to retrieve basic order details by ID.
    """
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        return Response({
            'id': order.id,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'shipment_id': order.shipment_id,
            'payment_id': order.payment_id,
        }, status=status.HTTP_200_OK)
