from flask import Blueprint, request, jsonify
from models.model import Cart, db
from producers.producer import publish, QUEUE_NAME
from auth_middleware import token_required
import requests
from datetime import datetime

cart_bp = Blueprint("cart_bp", __name__)
PRODUCT_SERVICE_URL = 'http://localhost:5001/products/'
ORDER_SERVICE_URL = 'http://localhost:5003/orders/'

def get_product_detail(product_id):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None


@cart_bp.route('/carts/add-to-cart', methods=['POST'])
@token_required
def add_to_cart():
    """API to add a product to the cart"""
    data = request.get_json()
    user_id = request.user.get("user_id") # get from claim in token
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not user_id or not product_id:
        return jsonify({"error": "User ID and Product ID are required"}), 400
    
    new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(new_cart_item)
    db.session.commit()

    # publish(queue=QUEUE_NAME, method="stock_update", body={"product_id": product_id, "quantity": quantity})

    return jsonify({"message": "Product added to cart, stock update request sent!"}), 201

@cart_bp.route('/carts/remove-from-cart/<cart_id>', methods=["POST"])
@token_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get(cart_id)

    if not cart_item:
        return jsonify({"message": "Cart item not found"}), 404
    
    product_id = cart_item.product_id
    quantity = cart_item.quantity

    db.session.delete(cart_item)
    db.session.commit()

    # publish(queue=QUEUE_NAME, method="remove_from_stock", body={"product_id": product_id, "quantity": quantity})

    return jsonify({"message": "Item removed from cart, stock updated"}), 200


@cart_bp.route('/carts/cart-items', methods=['GET'])
@token_required
def get_cart_item_of_user():
    user_id = request.user.get("user_id")

    if not user_id:
        return jsonify({"message": "Invalid or expired token"}), 401
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    detailed_cart = []
    for item in cart_items:
        product_details = get_product_detail(item.product_id)
        if product_details:
            detailed_cart.append({
                "cart_id": item.id,
                "products": product_details,
                "quantity": item.quantity,
                "added_at": item.added_at
            })
        
    return jsonify({
        "user_id": user_id,
        "cart_items": detailed_cart
    })

@cart_bp.route('/carts/cart-items/<cart_id>', methods=['GET'])
@token_required
def get_car_by_id(cart_id):
    user_id = request.user.get("user_id")

    if not user_id:
        return jsonify({"message": "Invalid or expired token"}), 401
    
    cart_item = Cart.query.get(cart_id)
    if not cart_item:
        return jsonify({"message": "Cart not found"}), 404
    
    product_detail = get_product_detail(cart_item.product_id)
    result = {
        "product": product_detail,
        "quantity": cart_item.quantity,
        "user_id": user_id,
        "added_at": cart_item.added_at
    }
    return jsonify(result), 200


@cart_bp.route('/carts/edit/<cart_id>', methods=['PUT'])
@token_required
def edit_cart(cart_id):
    user_id = request.user.get("user_id")

    if not user_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({"message": "Cart item not found"}), 404

    data = request.get_json()
    new_quantity = data.get("quantity")

    if new_quantity is None or new_quantity <= 0:
        return jsonify({"message": "Invalid quantity"}), 400
    
    quantity_diff = new_quantity - cart_item.quantity

    if quantity_diff != 0:
        cart_item.quantity = new_quantity
        db.session.commit()
        # publish(queue=QUEUE_NAME, method="remove_from_stock", body={"product_id": cart_item.product_id, "quantity": abs(quantity_diff)}) if new_quantity < 0 else publish(queue=QUEUE_NAME, method="stock_update", body={"product_id": cart_item.product_id, "quantity": quantity_diff})
        return jsonify({"message": "Cart item updated successfully"}), 200

    return jsonify({"message": "No changes made"}), 200
    
    
@cart_bp.route('/carts/total-price', methods=['POST'])
@token_required
def calculate_total_price():
    data = request.json

    if "items" not in data or not isinstance(data["items"], list):
        return jsonify({"error": "Invalid request body, must contain 'items' as a list"}), 400
    
    total_price = 0.0
    products_not_found = []

    for item in data['items']:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)

        if not product_id or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": f"Invalid product_id or quantity: {item}"}), 400
        
        product_detail = get_product_detail(product_id=product_id)
        total_price += product_detail.get("price", 0) * quantity
    result = {"total_price": total_price}

    return jsonify(result), 200

@cart_bp.route('/carts/filter-by-time', methods=['POST'])
@token_required
def filter_cart_by_time():
    start_date = request.args.get("start_date")  # Expected format: YYYY-MM-DD
    end_date = request.args.get("end_date")      # Expected format: YYYY-MM-DD

    if not start_date or not end_date:
        return jsonify({"error": "Both start_date and end_date are required"}), 400
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    cart_items = Cart.query.filter(Cart.added_at >= start_dt, Cart.added_at <= end_dt).all()
    if not cart_items:
        return jsonify({"message": "No cart items found in the given date range"}), 404
    
    cart_data = [
        {
            "cart_id": item.id,
            "user_id": item.user_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "added_at": item.added_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for item in cart_items
    ]

    return jsonify(cart_data), 200

        
@cart_bp.route('/carts/check-out', methods=['POST'])
@token_required
def check_out():
    data = request.json

    if "items" not in data or not isinstance(data["items"], list):
        return jsonify({"error": "Invalid request body, must contain 'items' as a list"}), 400
    
    for item in data['items']:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)

        if not product_id or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": f"Invalid product_id or quantity: {item}"}), 400
        
        publish(queue=QUEUE_NAME, method='stock_update', body={'product_id': product_id, 'quantity': quantity})

    headers = {"Authorization": request.headers.get('Authorization')}
    order_payload = {"items": data['items']}

    order_response = requests.post(f"{ORDER_SERVICE_URL}create-order", json=order_payload, headers=headers)

    if order_response.status_code != 201:
        return jsonify({"error": "Failed to create order", "details": order_response.json()}), order_response.status_code
    
    return jsonify(order_response.json()), 201