from flask import Blueprint, request, jsonify
from auth_middleware import token_required, admin_required
from bson.objectid import ObjectId
from database import mobiles_collections
from models.mobile import Mobile
from datetime import datetime

mobile_bp = Blueprint("mobile", __name__)

@mobile_bp.route("/mobiles", methods=["POST"])
def add_mobile():
    data = request.get_json()

    mobile = {
        "product_id": data["product_id"],
        "name": data["name"],
        "brand": data["brand"],
        "model": data["model"],
        "ram": data["ram"],
        "storage": data["storage"],
        "battery": data["battery"],
        "screen_size": data["screen_size"],
        "os": data["os"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    mobile_id = mobiles_collections.insert_one(mobile).inserted_id

    return jsonify({"message": "Mobile added successfully", "mobile_id": str(mobile_id)}), 201

@mobile_bp.route("/mobiles/<mobile_id>", methods = ['GET'])
def get_mobile_by_id(mobile_id):
    mobile = mobiles_collections.find_one({'product_id': mobile_id})

    if not mobile:
        return jsonify({"error": "Mobile not found"}), 404
    mobile["_id"] = str(mobile["_id"])
    return jsonify(mobile)

@mobile_bp.route('/mobiles', methods = ['GET'])
def get_all_mobiles():
    mobiles = list(mobiles_collections.find({}))
    for mobile in mobiles:
        mobile["_id"] = str(mobile["_id"])
    return jsonify(mobiles)