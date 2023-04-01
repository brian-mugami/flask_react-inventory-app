import uuid

from sqlalchemy.dialects.postgresql import UUID
from invapp.db import db
from datetime import datetime

class PurchaseModel(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True),index=True, unique=True, nullable=False,  default=uuid.uuid4)
    invoice_number = db.Column(db.String(256), nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    buying_price = db.Column(db.Float(precision=4), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    date_of_supply = db.Column(db.DateTime, default=datetime.utcnow())
    destination_type = db.Column(db.Enum("expense", "stores", name="destination_types"), default="stores", nullable=False)
    purchase_type = db.Column(db.Enum("cash", "credit", name="payment_types"), default="cash", nullable=False)
    update_date = db.Column(db.DateTime)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)

    items = db.relationship("ItemModel", back_populates="purchases")
    supplier = db.relationship("SupplierModel", back_populates="purchases")
    inventory_item = db.relationship("InventoryBalancesModel", back_populates="purchases", lazy="dynamic")
    expense_item = db.relationship("ExpensesModel", back_populates="expenses", lazy="dynamic")
    accounting = db.relationship("PurchaseAccountingModel", back_populates="purchases", lazy="dynamic")
    payments = db.relationship("PaymentModel", back_populates="purchase", lazy="dynamic")
    supplier_balance = db.relationship("SupplierBalanceModel", back_populates="purchase", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint('item_id', 'supplier_id', 'invoice_number', name="purchase_unique_constraint"),
    )

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_invoice_number(cls, num):
        return cls.query.filter_by(invoice_number=num).first()

    @property
    def amount(self):
        return self.quantity * self.buying_price

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

