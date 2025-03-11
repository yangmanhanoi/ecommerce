from flask import Blueprint, request, jsonify
from models.model import Order, OrderItem
from database import db
from auth_middleware import token_required, admin_required
import requests
import json
from datetime import datetime
from producers.producer import publish, CART_QUEUE_NAME, SHIPMENT_ORDER_QUEUE_NAME, PAYMENT_ORDER_QUEUE_NAME

order_bp = Blueprint("order_bp", __name__)
PRODUCT_SERVICE_URL = 'http://localhost:5001/products/'

def get_product_detail(product_id):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None

@order_bp.route('/orders/create-order', methods=['POST'])
@token_required
def create_order():
    data = request.get_json()

    user_id = request.user.get("user_id")
    cart_items = data.get('items')

    if not user_id or not cart_items:
        return jsonify({"message": "Missing user_id or items"}), 400
    
    total_price = 0
    order_items = []

    for item in cart_items:
        product_id = item['product_id']
        quantity = item['quantity']

        product_data = get_product_detail(product_id)

        price = product_data['price']
        total_price += price * quantity

        order_items.append(OrderItem(product_id=product_id, quantity=quantity, price=price))
    
    new_order = Order(user_id=user_id, total_price=total_price, order_items=order_items)
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Order created successfully", "order_id": new_order.id, "total_price": total_price}), 201

@order_bp.route('/orders/get-by-id/<order_id>', methods=['GET'])
@token_required
def get_order_by_id(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict()), 200

@order_bp.route('/orders/user', methods=['GET'])
@token_required
def get_list_order():
    user_id = request.user.get("user_id")
    status = request.args.get("status", type=str)
    start_date = request.args.get("start_date", type=str)
    end_date = request.args.get("end_date", type=str)

    query = Order.query

    if user_id:
        query = query.filter(user_id==user_id)
    if status:
        query = query.filter(status==status)
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Order.created_at.between(start_date, end_date))
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    
    orders = query.all()
    return jsonify([order.to_dict() for order in orders]), 200

@order_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    data = request.json
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    order.status = new_status
    db.session.commit()
    return jsonify({"message": "Order status updated", "order": order.to_dict()}), 200

@order_bp.route('/orders/<int:order_id>/cancel', methods=['PUT'])
@token_required
def cancel_order(order_id):
    user_id = request.user.get('user_id')

    order = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if not Order:
        return jsonify({"error": "Order not found or not yours"}), 404
    
    if order.status != 'pending':
        return jsonify({"error": "Only pending orders can be canceled"}), 400

    order.status = 'canceled'
    db.session.commit()

    for item in order.order_items:
        product_id = item.product_id
        quantity = item.quantity
        publish(queue=CART_QUEUE_NAME, method='remove_from_stock', body={'product_id': product_id, 'quantity': quantity})

    return jsonify({"message": "Order canceled and stock returned"}), 200

@order_bp.route('/orders/<int:order_id>/accept', methods=['PUT'])
@admin_required
def accept_order(order_id):
    """API to accept an order and trigger shipment creation"""
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    if order.status != "pending":
        return jsonify({"error": "Order is not in a pending state"}), 400
    
    # Update order status to "accepted"
    order.status = "accepted"
    db.session.commit()

    # update lấy thêm address_id của user cho hơp logic
    publish(queue=SHIPMENT_ORDER_QUEUE_NAME, method='create_shipment', body={'order_id': order_id, 'user_id': order.user_id})
    return jsonify({"message": "Order accepted", "order_id": order_id}), 200

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
def purchase_request(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict()), 200

