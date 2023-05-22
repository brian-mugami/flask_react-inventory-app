import uuid
from sqlalchemy.dialects.postgresql import UUID
from backend.invapp.db import db
from datetime import datetime

class ReceiptModel(db.Model):
    __tablename__ = "receipts"

    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True),index=True, unique=True, nullable=False,  default=uuid.uuid4)
    receipt_number = db.Column(db.Integer, db.Sequence("customers_id_seq", start=100, increment=5), nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    currency = db.Column(db.String(10), nullable=False, default="KES")
    date = db.Column(db.DateTime, default=datetime.utcnow())
    update_date = db.Column(db.DateTime)
    amount = db.Column(db.Float(precision=4), default=0.00)
    accounted_status = db.Column(db.Enum("fully_accounted", "partially_accounted", "not_accounted", name="accounting_status"),
                          default="not_accounted")
    status = db.Column(db.Enum("fully paid", "partially paid", "not paid", "over paid", name="invoice_status"),
                       default="not paid")
    sale_type = db.Column(db.Enum("cash", "credit", name="sales_header_types"), default="cash", nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    voided = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(256))
    customer = db.relationship("CustomerModel", back_populates="receipt")
    customer_balance = db.relationship("CustomerBalanceModel", back_populates="receipt", cascade="all, delete-orphan")
    bank_balance = db.relationship("BankBalanceModel", back_populates="receipt", cascade="all, delete-orphan")
    accounting = db.relationship("SalesAccountingModel", back_populates="receipt", cascade="all, delete-orphan")
    received = db.relationship("CustomerPaymentModel", back_populates="receipt", cascade="all, delete-orphan")
    sale_items = db.relationship("SalesModel", back_populates="receipt", cascade="all, delete-orphan")
    inventory_item = db.relationship("InventoryBalancesModel", back_populates="receipt")

    __table_args__ = (
        db.UniqueConstraint('customer_id', "currency", 'receipt_number', name="sales_header_constraint"),
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def void_receipt(self):
        self.voided = True
        self.update_db()