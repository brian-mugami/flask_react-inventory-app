import uuid

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
from invapp.db import db
from datetime import datetime
import enum

class PurchaseType(enum.Enum):
    cash = "cash"
    credit = "credit"


class PurchaseModel(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True), unique=True, nullable=False,  default=uuid.uuid4)
    invoice_number = db.Column(db.String(256), nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    buying_price = db.Column(db.Float(precision=4), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    date_of_supply = db.Column(db.DateTime, default=datetime.utcnow())
    purchase_type = db.Column(db.Enum("cash", "credit", name="payment_types"), default="cash", nullable=False)
    update_date = db.Column(db.DateTime)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)

    items = db.relationship("ItemModel", back_populates="purchases")
    supplier = db.relationship("SupplierModel", back_populates="purchases")
    inventory_item = db.relationship("InventoryBalancesModel", back_populates="purchases", lazy="dynamic")
    accounting = db.relationship("PurchaseAccountingModel", back_populates="purchases", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint('item_id', 'supplier_id', 'invoice_number', name="purchase_unique_constraint"),
    )

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_invoice_number(cls, num):
        return cls.query.filter_by(invoice_number=num).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

