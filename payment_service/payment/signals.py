from django.conf import settings
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from django.http import HttpResponse
import requests
from producer import publish, PAYMENT_ORDER_QUEUE_NAME
@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn = sender
    item_name = ipn.item_name
    amount = ipn.mc_gross
    invoice_id = ipn.invoice
    payer_email = ipn.payer_email
    print(ipn)
    print(f"Amount: {ipn.mc_gross}, item_name: {item_name}, payer_email: {payer_email}")
    if invoice_id and amount and item_name:
        order_id = int(item_name[5:])
        publish(queue=PAYMENT_ORDER_QUEUE_NAME, method='payment-status', body={'order_id': order_id})