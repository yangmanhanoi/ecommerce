from flask import Flask
from database import db
from routes.order_routes import order_bp

app = Flask(__name__)
app.register_blueprint(order_bp)

# PostgreSQL Configuration
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://namdt25:namdt25@localhost:5432/orders_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5003, debug=True)