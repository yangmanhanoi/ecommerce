import pika
import json
import datetime
import random
import string
from app import db, app
from models.model import Shipment

RABBITMQ_HOST = 'localhost'
SHIPMENT_ORDER_QUEUE_NAME = 'shipment-order'
credentials = pika.PlainCredentials("namdt25", "namdt25")
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST, 
    port=5672,  # Default RabbitMQ port
    credentials=credentials
)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
channel.queue_declare(queue=SHIPMENT_ORDER_QUEUE_NAME)

def generate_tracking_number():
    """Generate a random tracking number"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def create_shipment(order_id, user_id):
    tracking_number = generate_tracking_number()
    estimated_delivery = datetime.datetime.utcnow() + datetime.timedelta(days=3)  # 3 days shipping
    with app.app_context():
        new_shipment = Shipment(
            order_id=order_id,
            user_id=user_id,
            tracking_number=tracking_number,
            status="pending",
            estimated_delivery=estimated_delivery
        )
        db.session.add(new_shipment)
        db.session.commit()

        print(f"✅ Shipment created for order {order_id} with tracking {tracking_number}")

def callback(ch, method, properties, body):
    """Process messages from RabbitMQ"""
    data = json.loads(body)
    print(f"📥 Received message: {data}")

    if properties.type == "create_shipment":
        order_id = data["order_id"]
        user_id = data['user_id']
        create_shipment(order_id, user_id)
    
channel.basic_consume(queue=SHIPMENT_ORDER_QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print("🎧 Listening for order acceptance messages...")
channel.start_consuming()