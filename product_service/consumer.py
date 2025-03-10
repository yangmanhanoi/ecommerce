import pika
import json
from database import products_collection
from bson.objectid import ObjectId

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'add-to-cart'
credentials = pika.PlainCredentials("namdt25", "namdt25")
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST, 
    port=5672,  # Default RabbitMQ port
    credentials=credentials
)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

def reduce_stock(product_id, quantity):
    """Reduce stock in MongoDB"""
    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if product:
        new_stock = max(0, product["stock"] - quantity)
        products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": {"stock": new_stock}})
        print(f"✅ Stock updated: {product_id} -> {new_stock}")
    else:
        print(f"⚠️ Product {product_id} not found!")

def remove_from_stock(product_id, quantity):
    """ Return item into stock """
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if product:
        new_stock = product["stock"] + quantity
        products_collection.update_one({"_id": ObjectId(product_id)}, { "$set": {"stock": new_stock}})
        print(f"✅ Stock updated: {product_id} -> {new_stock}")
    else:
        print(f"⚠️ Product {product_id} not found!")


def callback(ch, method, properties, body):
    """RabbitMQ message processing"""
    data = json.loads(body)
    print(f"📥 Received message: {data}")

    if properties.type == "stock_update":
        reduce_stock(data["product_id"], data["quantity"])
    elif properties.type == "remove_from_stock":
        remove_from_stock(data["product_id"], data["quantity"])
    else:
        print(f"⚠️ Unknown message type: {properties.type}")




channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print("🟢 Waiting for stock update messages...")

channel.start_consuming()



