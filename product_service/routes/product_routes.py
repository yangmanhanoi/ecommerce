from flask import Blueprint, request, jsonify
from auth_middleware import token_required, admin_required
from bson.objectid import ObjectId
from database import products_collection
from models.product import Book, Clothes, Mobile
# Create a Blueprint for products
product_bp = Blueprint("product", __name__)

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
    product = None

    if category == "Book":
        product = Book(data["name"], data["price"], data["stock"], data["author"], data["isbn"], data["published_year"])
        
    elif category == "Clothes":
        product = Clothes(data["name"], data["price"], data["stock"], data["size"], data["color"], data["material"])
        
    elif category == "Mobile":
        product = Mobile(data["name"], data["price"], data["stock"], data["ram"], data["storage"], data["battery"])
        
    else:
        return jsonify({"error": "Invalid category"}), 400
    
    products_collection.insert_one(product.to_dict())
    return jsonify({"message": "Product added successfully"}), 201


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