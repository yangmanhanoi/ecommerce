import pika
import json
from app import app, db
from models.model import Order

STATUS_MAPPING = {
    'shipped': 'shipped',
    'in_transit': 'shipped',
    'out_of_delivery': 'shipping',
    'delivered': 'delivered',
    'returned': 'cancelled'
}
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

def callback(ch, method, properties, body):

    """Process messages from RabbitMQ"""
    with app.app_context():
        try:
            data = json.loads(body)
            print(f"📥 Received message: {data}")

            if properties.type == 'status_update':
                order_id = data['order_id']
                user_id = data['user_id']
                shipment_status = data['status']
                order = Order.query.get(order_id)

                if not order:
                    print(f"❌ Order ID {order_id} not found.")
                    return
                if order.user_id != user_id:
                    print(f"⚠️ Order {order_id} does not belong to user {user_id}. Skipping update.")
                    return
                if shipment_status not in STATUS_MAPPING:
                    print(f"❌ Invalid shipment status: {shipment_status}")
                    return
                
                order.status = STATUS_MAPPING[shipment_status]
                db.session.commit()
                print(f"✅ Order {order_id} updated to status: {order.status}") 
        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")

channel.basic_consume(queue=SHIPMENT_ORDER_QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print("🎧 Listening for order status change messages...")
channel.start_consuming()