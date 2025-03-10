from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from database import db
from routes.cart_routes import cart_bp
import os

app = Flask(__name__)
app.register_blueprint(cart_bp)
# PostgreSQL Configuration
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://namdt25:namdt25@localhost:5432/orders_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5002,debug=True)