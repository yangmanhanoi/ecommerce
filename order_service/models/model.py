from database import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # From auth_service
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, shipped, delivered, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "items": [item.to_dict() for item in self.order_items]
        }

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.String, nullable=False)  # From product_service
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship("Order", back_populates="order_items")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price
        }
    
# pending: Order has been created but not processed yet.
# confirmed: Payment has been verified, and order is ready for shipment.
# shipped: The order has been shipped (updated when shipment status is "shipped").
# delivered: Order has been successfully delivered to the customer.
# cancelled: Order was canceled (before shipment or due to return).