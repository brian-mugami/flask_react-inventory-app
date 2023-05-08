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
    accounting_status = db.Column(db.Enum("account","void", name="accounting_rules"), default="account")
    accounted = db.Column(db.Enum("fully_accounted", "partially_accounted", "not_accounted",name="accounting_status"), default="not_accounted")
    status = db.Column(db.Enum("fully paid", "partially paid", "not paid", "over paid",name="invoice_status"), default="not paid")
    matched_to_lines = db.Column(db.Enum("matched", "unmatched","partially matched", name="invoice_matched_types"), default="unmatched", nullable=False)
    destination_type = db.Column(db.Enum("expense", "stores", name="destination_types"), default="stores", nullable=False)
    purchase_type = db.Column(db.Enum("cash", "credit", name="payment_types"), default="cash", nullable=False)
    update_date = db.Column(db.DateTime)
    voided = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(256))
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    expense_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)

    purchase_items = db.relationship("PurchaseModel", back_populates="invoice", cascade="all, delete-orphan")
    supplier = db.relationship("SupplierModel", back_populates="invoice")
    supplier_balance = db.relationship("SupplierBalanceModel", back_populates="invoice", lazy="dynamic", cascade="all, delete-orphan")

    expense_account = db.relationship("AccountModel", back_populates="expense_invoice")
    inventory_item = db.relationship("InventoryBalancesModel", back_populates="invoice", lazy="dynamic", cascade="all, delete-orphan")
    bank_balance = db.relationship("BankBalanceModel", back_populates="invoice", lazy="dynamic",cascade="all, delete-orphan")
    expense_item = db.relationship("ExpensesModel", back_populates="invoice", lazy="dynamic", cascade="all, delete-orphan")
    accounting = db.relationship("PurchaseAccountingModel", back_populates="invoice", lazy="dynamic", cascade="all, delete-orphan")
    payments = db.relationship("SupplierPaymentModel", back_populates="invoice", lazy="dynamic", cascade="all, delete-orphan")

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

    def void_invoice(self):
        self.voided = True
        db.session.commit()