from flask import Flask
from database import db
from routes.shipment_routes import shipment_bp
from flask_migrate import Migrate
app = Flask(__name__)
app.register_blueprint(shipment_bp)

# PostgreSQL Configuration
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://namdt25:namdt25@localhost:5432/orders_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)
# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=5004,debug=True)