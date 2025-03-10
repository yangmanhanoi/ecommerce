import json
import pika
from django.conf import settings
import uuid
from django.urls import reverse
RABBITMQ_HOST = 'localhost'
PAYMENT_ORDER_QUEUE_NAME = 'payment-order'
credentials = pika.PlainCredentials("namdt25", "namdt25")
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST, 
    port=5672,  # Default RabbitMQ port
    credentials=credentials
)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
channel.queue_declare(queue=PAYMENT_ORDER_QUEUE_NAME)

def validate(data):
    order_id = data['order_id']
    user_id = data['user_id']
    total_price = data['total_price']

    if not order_id:
        print(f"❌ Order ID {order_id} not found.")
        return False

def paypal_payment(data):
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': data['total_price'],
        'item_name': data['order_id'],
        'invoice': str(uuid.uuid4()),
        'currency_code':'USE',
        'notify_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('paypal-ipn')),
        'return_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('paypal-success')),
        'cancel_url': '{}{}'.format(settings.NGROK_STATIC_URL, reverse('paypal-cancel')),
    }

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"📥 Received message: {data}")

    if properties.type == 'purchase-request':
        if validate(data=data) == False:
            return
        

        


channel.basic_consume(queue=PAYMENT_ORDER_QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print("🎧 Listening for payment request messages...")
channel.start_consuming()