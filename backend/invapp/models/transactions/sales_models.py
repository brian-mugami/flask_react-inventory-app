import uuid
from sqlalchemy.dialects.postgresql import UUID
from invapp.db import db
from datetime import datetime

class SalesModel(db.Model):
    __tablename__ = "sales"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_number = db.Column(db.String(256), nullable=False, index=True, unique=True)
    description = db.Column(db.String(256), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float(precision=4), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    date_sold = db.Column(db.DateTime, default=datetime.utcnow())

    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    #payment_type_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)