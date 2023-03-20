import uuid

from invapp.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class InventoryBalancesModel(db.Model):
    __tablename__ = "inventory_balances"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False, default=0.00)
    date = db.Column(db.DateTime, default=datetime.utcnow())