from flask import Flask, request, jsonify
from database import db
from routes.book_routes import book_bp


app = Flask(__name__)

app.register_blueprint(book_bp)

if __name__ == '__main__':
    app.run(port=5005, debug=True)