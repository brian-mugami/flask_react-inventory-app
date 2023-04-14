import uuid

from invapp.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class PurchaseAccountingModel(db.Model):
    __tablename__ = "purchase_accounting"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    credit_amount = db.Column(db.Float,default=0.000)
    debit_amount = db.Column(db.Float,default=0.000)
    update_date = db.Column(db.DateTime)
    credit_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    debit_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))

    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id", ondelete='CASCADE'))

    invoice = db.relationship("InvoiceModel", back_populates="accounting")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

class SupplierPayAccountingModel(db.Model):
    __tablename__ = "supplier_payment_accounting"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    credit_amount = db.Column(db.Float,default=0.000)
    debit_amount = db.Column(db.Float,default=0.000)
    update_date = db.Column(db.DateTime)
    credit_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete='SET NULL'))
    debit_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete='SET NULL'))

    payment_id = db.Column(db.Integer, db.ForeignKey("supplier_payments.id", ondelete="CASCADE"), nullable=False)
    balance_id = db.Column(db.Integer, db.ForeignKey("supplier_balances.id",ondelete="CASCADE"), nullable=False)

    payments = db.relationship("SupplierPaymentModel", back_populates="accounting")
    balance = db.relationship("SupplierBalanceModel", back_populates="accounting")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()