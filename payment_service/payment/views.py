from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import requests

ORDER_SERVICE_URL = 'http://localhost:5003/orders/'

def get_order_detail(order_id, headers):
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/{order_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None

def payment(request, order_id):
    headers = {"Authorization": request.headers.get('Authorization')}
    order_detail = get_order_detail(order_id, headers)
    if not order_detail:
        return jsonify({"error": "Order not found"}), 404
    print(order_detail)
    total_price = order_detail.get('total_price')
    item_name = f"ORDER{order_detail.get('id'):05d}"
    print(f"price: {total_price}, id: {item_name}")
    if not total_price or not item_name:
        return jsonify({"error": "Order not found"}), 404
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total_price,
        'item_name': item_name,
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