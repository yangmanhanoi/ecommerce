from flask import Blueprint, request, jsonify
from database import db
from models.model import Shipment
from auth_middleware import token_required, admin_required
from datetime import datetime
from producer import publish, SHIPMENT_ORDER_QUEUE_NAME
shipment_bp = Blueprint("shipment_bp", __name__)

@shipment_bp.route('/shipments/admin/<int:shipment_id>', methods=['GET'])
@admin_required
def get_shipment(shipment_id):
    shipment = Shipment.query.get(shipment_id)

    if not shipment:
        return jsonify({"error": "Shipment not found"}), 404
    return jsonify({
        'id': shipment.id,
        "order_id": shipment.order_id,
        'user_id': shipment.user_id,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "estimated_delivery": shipment.estimated_delivery,
        "shipped_at": shipment.shipped_at,
        "delivered_at": shipment.delivered_at
    })

@shipment_bp.route('/shipments/customer', methods=['GET'])
@token_required
def get_all_customer_shipment():
    status = request.args.get('status')
    user_id = request.user.get('user_id')

    query = Shipment.query

    if status:
        query = query.filter_by(status=status)
    if user_id:
        query = query.filter_by(user_id=user_id)
    shipments = query.all()

    return jsonify([{
        'id': s.id,
        "order_id": s.order_id,
        'user_id': user_id,
        "status": s.status,
        'estimated_delivery': s.estimated_delivery
    } for s in shipments])

@shipment_bp.route('/shipments/<string:tracking_number>', methods=['GET'])
@token_required
def track_shipment(tracking_number):
    user_id = request.user.get('user_id')

    shipment = Shipment.query.filter_by(tracking_number=tracking_number).first()
    if not shipment:
        return jsonify({"error": "Tracking number not found"}), 404
    return jsonify({
        "id": shipment.id,
        "order_id": shipment.order_id,
        "tracking_number": shipment.tracking_number,
        "user_id": shipment.user_id,
        "status": shipment.status,
        "estimated_delivery": shipment.estimated_delivery,
        "shipped_at": shipment.shipped_at,
        "delivered_at": shipment.delivered_at
    })

@shipment_bp.route('/shipments/<int:shipment_id>/status', methods=['PUT'])
@admin_required
def update_shipment_status(shipment_id):
    data = request.json
    new_status = data.get('status')

    shipment = Shipment.query.get(shipment_id)
    if not shipment:
        return jsonify({"error": "Shipment not found"}), 404
    
    shipment.status = new_status

    if new_status == "shipped":
        shipment.shipped_at = datetime.utcnow()
    elif new_status == "delivered":
        shipment.delivered_at = datetime.utcnow()

    # send message
    publish(queue=SHIPMENT_ORDER_QUEUE_NAME, method='status_update', body={'status': new_status, 'order_id': shipment.order_id, 'user_id': shipment.user_id})

    db.session.commit()
    return jsonify({"message": f"Shipment status updated to {new_status}"}), 200