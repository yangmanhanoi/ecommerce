from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import requests
import json
ORDER_SERVICE_URL = 'http://localhost:5003/orders/'
SHIP_SERVICE_URL = 'http://localhost:5003/api/shipments/admin/'
CART_SERVICE_URL = 'http://localhost:8101/api/carts'
def get_cart_price(items):
    try:
        response = requests.post(f"{CART_SERVICE_URL}/total-price",
                                json={"items": items},  # Send items as JSON body
                                headers={"Content-Type": "application/json"} )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None
    
def get_shipment_detail(shipment_id):
    try:
        response = requests.get(f"{SHIP_SERVICE_URL}{shipment_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None
def get_order_detail(order_id, headers):
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/{order_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None

def payment(request, shipment_id):
    shipment_detail = get_shipment_detail(shipment_id=shipment_id)

    if not shipment_detail:
        return JsonResponse({"error": "Shipment not found"}), 404
    try:
    
        items = [{
            "product_id": "67e18794781709f814a79539",
            "quantity": 1
        }]  # Extract items list
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    cart_price = get_cart_price(items=items)
    print(cart_price)
    print(shipment_detail)
    total_price = float(cart_price.get('total_price', 0)) + float(shipment_detail.get("shipping_cost", 0))
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total_price,
        'item_name': "Product1111",
        'invoice': str(uuid.uuid4()),
        'currency_code':'USD',
        'notify_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('paypal-ipn')),
        'return_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('payment_success')),
        'cancel_return': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('payment_failed')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'paypal_checkout.html', {"form": form})

def payment_success(request):
    return render(request, 'payment_success.html', {})

def payment_failed(request):
    return render(request, 'payment_failed.html', {})