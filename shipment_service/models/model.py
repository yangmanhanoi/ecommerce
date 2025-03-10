from database import db

class Shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tracking_number = db.Column(db.String, unique=True, nullable=True)
    status = db.Column(db.String, default="pending")  # e.g., pending, shipped, delivered
    estimated_delivery = db.Column(db.DateTime, nullable=True)
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)

# pending: Shipment is created but not yet picked up by the carrier.
# in_transit: Shipment is on the way to the delivery address.
# out_for_delivery: Shipment has arrived at the local facility and is being delivered.
# delivered: Shipment has reached the customer.
# failed
# returned