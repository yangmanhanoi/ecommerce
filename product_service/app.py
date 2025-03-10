from flask import Flask, request, jsonify
from pymongo import MongoClient
from routes.product_routes import product_bp
from database import db
app = Flask(__name__)


app.register_blueprint(product_bp)


@app.route('/')
def hello():
    return 'Hello, Nam'

if __name__ == '__main__':
    app.run(port=5001, debug=True)