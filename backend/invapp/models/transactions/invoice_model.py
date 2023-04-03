import uuid
from sqlalchemy.dialects.postgresql import UUID
from invapp.db import db
from datetime import datetime

class InvoiceModel(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True),index=True, unique=True, nullable=False,  default=uuid.uuid4)
    invoice_number = db.Column(db.String(256), nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    currency = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    accounted = db.Column(db.Boolean,default=False)
    matched_to_lines = db.Column(db.Enum("matched", "unmatched","partially_matched", name="invoice_matched_types"), default="unmatched", nullable=False)
    destination_type = db.Column(db.Enum("expense", "stores", name="destination_types"), default="stores", nullable=False)
    purchase_type = db.Column(db.Enum("cash", "credit", name="payment_types"), default="cash", nullable=False)
    update_date = db.Column(db.DateTime)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)

    purchase_items = db.relationship("PurchaseModel", back_populates="invoice")
    supplier = db.relationship("SupplierModel", back_populates="invoice")

    inventory_item = db.relationship("InventoryBalancesModel", back_populates="invoice", lazy="dynamic")
    expense_item = db.relationship("ExpensesModel", back_populates="invoice", lazy="dynamic")
    accounting = db.relationship("PurchaseAccountingModel", back_populates="invoice", lazy="dynamic")
    payments = db.relationship("PaymentModel", back_populates="invoice", lazy="dynamic")
    supplier_balance = db.relationship("SupplierBalanceModel", back_populates="invoice", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint('invoice_number','currency', 'supplier_id', name="purchase_unique_constraint"),
    )
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()