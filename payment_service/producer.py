import pika
import json

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

def publish(queue, method, body):
    channel.queue_declare(queue=queue)

    properties = pika.BasicProperties(type=method)
    channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(body), properties=properties)

    print(f"📤 Sent message to {queue}: {body}")