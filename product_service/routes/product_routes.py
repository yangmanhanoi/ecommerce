from flask import Blueprint, request, jsonify
from auth_middleware import token_required, admin_required
from bson.objectid import ObjectId
from database import products_collection
from models.product import Book, Clothes, Mobile
from datetime import datetime
import requests
# Create a Blueprint for products
product_bp = Blueprint("product", __name__)


BOOK_SERVICE_URL = 'http://localhost:5005'
MOBILE_SERVICE_URL = 'http://localhost:5006'
CLOTHES_SERVICE_URL = 'http://localhost:5007'
RECOMMENDATION_SERVICE_URL = "http://localhost:5000/recommend"

@product_bp.route("/products", methods=["GET"])
def get_all_products():
    products = list(products_collection.find({}))
    # Convert `_id` from ObjectId to string
    for product in products:
        product["_id"] = str(product["_id"])
    return jsonify(products), 200

# add new product
@product_bp.route("/products/add-item", methods=["POST"])
@admin_required
def add_product():
    data = request.get_json()
    category = data.get("category")
    product = {
        "name": data["name"],
        "category": data["category"],
        "price": data["price"],
        "stock": data["stock"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    product_id = products_collection.insert_one(product).inserted_id

    if category == "Book":
        book_data = {
            "product_id": str(product_id),
            "name": data["name"],
            "author_ids": data["author_ids"],  # Danh sách ID tác giả
            "publisher": data["publisher"],
            "isbn": data["isbn"],
            "pages": data["pages"],
            "language": data["language"],
            "published_year": data["published_year"]
        }

        response = requests.post(f"{BOOK_SERVICE_URL}/books", json=book_data)
        if response.status_code != 201:
            return jsonify({"error": "Failed to save book details"}), 500
    elif category == "Clothes":
        clothes_data = {
            "product_id": str(product_id),
            "name": data["name"],
            "brand_id": data["brand_id"],
            "size": data["size"],
            "color": data["color"],
            "material": data["material"],
            "gender": data["gender"]
        }

        response = requests.post(f"{CLOTHES_SERVICE_URL}/clothes", json=clothes_data)
        if response.status_code != 201:
            return jsonify({"error": "Failed to save clothes details"}), 500
        
    elif category == "Mobile":
        mobile_data = {
            "product_id": str(product_id),
            "name": data["name"],
            "brand": data["brand"],
            "model": data["model"],
            "ram": data["ram"],
            "storage": data["storage"],
            "battery": data["battery"],
            "screen_size": data["screen_size"],
            "os": data["os"]
        }
        response = requests.post(f"{MOBILE_SERVICE_URL}/mobiles", json=mobile_data)
        if response.status_code != 201:
            return jsonify({"error": "Failed to save mobile details"}), 500
        
    else:
        return jsonify({"error": "Invalid category"}), 400
    
    return jsonify({"message": "Item added successfully!", "product_id": str(product_id)}), 201


# Get product by id
@product_bp.route("/products/<product_id>", methods=['GET'])
def get_product_by_id(product_id):
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if not product:
        return jsonify({"error": "Product not found"}), 404
    product["_id"] = str(product["_id"])  # Convert ObjectId to string
    return jsonify(product)

# Delete a product (Admin only)
@product_bp.route("/products/<product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    result = products_collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product deleted successfully"}), 200

# Update product by id
@product_bp.route("/products/<product_id>", methods=['PUT'])
@admin_required
def update_product(product_id):
    data = request.get_json()

    # Ensure product exists
    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Update fields
    update_data = {}
    for key in ["name", "price", "stock", "category"]:
        if key in data:
            update_data[key] = data[key]

    if product["category"] == "Book":
        book_fields = ["author", "isbn", "published_year"]
        update_data.update({key: data[key] for key in book_fields if key in data})
    elif product["category"] == "Clothes":
        clothes_fields = ["size", "color", "material"]
        update_data.update({key: data[key] for key in clothes_fields if key in data})
    elif product["category"] == "Mobile":
        mobile_fields = ["ram", "storage", "battery"]
        update_data.update({key: data[key] for key in mobile_fields if key in data})
    if not update_data:
        return jsonify({"error": "No valid fields provided for update"}), 400
    
    products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
    return jsonify({"message": "Product updated successfully"}), 200

# Get product by category
@product_bp.route("/products/category/<category_name>", methods=['GET'])
def get_products_by_category(category_name):
    products = list(products_collection.find({"category": category_name}))
    for product in products:
        product["_id"] = str(product["_id"])
    return jsonify(products), 200

# 2️⃣ Search Products by Name
@product_bp.route("/products/search", methods=["GET"])
def search_products():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    products = list(products_collection.find({"name": {"$regex": query, "$options": "i"}}))
    for product in products:
        product["_id"] = str(product["_id"])
    
    return jsonify(products), 200

# 3️⃣ Filter Products by Price Range
@product_bp.route("/products/filter", methods=["GET"])
def filter_products():
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    
    filter_query = {}
    if min_price is not None:
        filter_query["price"] = {"$gte": min_price}
    if max_price is not None:
        if "price" in filter_query:
            filter_query["price"]["$lte"] = max_price
        else:
            filter_query["price"] = {"$lte": max_price}

    products = list(products_collection.find(filter_query))
    for product in products:
        product["_id"] = str(product["_id"])
    
    return jsonify(products), 200


@product_bp.route("/products/comment", methods=["POST"])
def add_comment(product_id):
    data = request.get_json()
    user_id = data.get("user_id", "").strip()
    product_id = data.get("product_id", "").strip()
    comment = data.get("comment", "").strip()

    if not user_id or not product_id or not comment:
        return jsonify({"error": "Missing user_id, product_id, or comment"}), 400

    # Call sentiment prediction API
    response = requests.post(f"{RECOMMENDATION_SERVICE_URL}/predict", json={
        "user_id": user_id,
        "product_id": product_id,
        "comment": comment
    })

    if response.status_code == 200:
        return jsonify(response.json()), 201
    else:
        return jsonify({"error": "Failed to analyze sentiment"}), 500


@product_bp.route("/products/recommend", methods=["GET"])
def recommend_books():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Call the Flask recommendation API
    response = requests.get(f"{RECOMMENDATION_SERVICE_URL}?user_id={user_id}")

    if response.status_code == 200:
        recommended_books = response.json()

        # Fetch book details from MongoDB
        book_ids = [ObjectId(book["book_id"]) for book in recommended_books]
        books = list(products_collection.find({"_id": {"$in": book_ids}, "category": "Book"}))

        # Convert `_id` from ObjectId to string
        for book in books:
            book["_id"] = str(book["_id"])

        return jsonify(books), 200
    else:
        return jsonify({"error": "Failed to fetch recommendations"}), response.status_code