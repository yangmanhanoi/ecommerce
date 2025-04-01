from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from database import books_collection, author_collection
from models.book import Book, Author
from auth_middleware import admin_required, token_required
# Create a Blueprint for products
book_bp = Blueprint("book", __name__)
def serialize_book(book):
    book["_id"] = str(book["_id"])  # Chuyển ObjectId của sách thành string
    book["author_ids"] = [str(author_id) for author_id in book["author_ids"]]  # Chuyển danh sách ObjectId của author_ids
    return book
# Thêm Author
@book_bp.route("/authors", methods=["POST"])
@admin_required
def add_author():
    data = request.json
    author = Author(name=data["name"], birth_year=data["birth_year"], nationality=data['nationality'])
    author_id = author_collection.insert_one(author.to_dict()).inserted_id
    return jsonify({"message": "Author added successfully!", "author_id": str(author_id)}), 201

# Lấy danh sách Author
@book_bp.route("/authors", methods=["GET"])
def get_authors():
    authors = list(author_collection.find({}, {"_id": 1, "name": 1, "bio": 1}))
    for author in authors:
        author["_id"] = str(author["_id"])
    return jsonify(authors), 200

@book_bp.route('/books', methods=['POST'])
def add_book():
    data = request.json
    book = Book(
        product_id=data['product_id'],
        name=data["name"],
        author_ids=data["author_ids"],  # Nhận danh sách ID của tác giả
        publisher=data["publisher"],
        isbn=data["isbn"],
        pages=data["pages"],
        language=data["language"],
        published_year=data["published_year"],
    )
    book_id = books_collection.insert_one(book.to_dict()).inserted_id
    return jsonify({"message": "Book added successfully!", "book_id": str(book_id)}), 201

@book_bp.route('/books/<book_id>', methods=['GET'])
def get_book_by_id(book_id):
    book = books_collection.find_one({"product_id": book_id})
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(serialize_book(book))

@book_bp.route("/books", methods=["GET"])
def get_all_books():
    books = list(books_collection.find({}))
    for book in books:
        serialize_book(book=book)
    return jsonify(books)