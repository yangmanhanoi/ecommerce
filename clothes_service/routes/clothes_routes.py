from flask import Blueprint, request, jsonify
from models.clothes import Clothes, Brand
from bson.objectid import ObjectId
from database import clothes_collection, brands_collection

clothes_bp = Blueprint("clothes", __name__)

@clothes_bp.route("/brands", methods=["POST"])
def add_brand():
    data = request.get_json()
    brand = Brand(name=data["name"], origin_country=data.get("origin_country", ""), description=data.get("description", ""))
    brand_id = brands_collection.insert_one(brand.to_dict()).inserted_id
    return jsonify({"message": "Brand added successfully", "brand_id": str(brand_id)}), 201

@clothes_bp.route("/clothes/<clothes_id>", methods = ['GET'])
def get_clothes(clothes_id):
    clothes = clothes_collection.find_one({"product_id": clothes_id})
    if not clothes:
        return jsonify({"error": "Clothes not found"}), 404

    brand = brands_collection.find_one({"_id": ObjectId(clothes["brand_id"])})

    return jsonify({
        "brand": brand["name"] if brand else "Unknown",
        "origin_country": brand["origin_country"] if brand else "Unknown",
        "size": clothes["size"],
        "color": clothes["color"],
        "gender": clothes["gender"]
    })

@clothes_bp.route("/clothes", methods=["POST"])
def add_clothes():
    data = request.get_json()
    clothes = Clothes(
        product_id=data["product_id"],
        brand_id=data["brand_id"],
        size=data["size"],
        color=data["color"],
        gender=data["gender"],
        material=data["material"]
    )
    clothes_id = clothes_collection.insert_one(clothes.to_dict()).inserted_id
    return jsonify({"message": "Clothes added successfully", "clothes_id": str(clothes_id)}), 201