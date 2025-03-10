from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def payment(request):
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '100',
        'item_name': '00001',
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