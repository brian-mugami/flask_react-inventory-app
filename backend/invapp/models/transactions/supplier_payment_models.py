import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from invapp.db import db

class SupplierPaymentModel(db.Model):
    __tablename__ = "supplier_payments"
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    payment_description = db.Column(db.String(256))
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default="KES")
    date = db.Column(db.DateTime, default=datetime.utcnow())
    update_date = db.Column(db.DateTime)
    approval_status = db.Column(db.Enum('pending approval', 'approved', 'rejected', name='supplier_payment_approval_status'), nullable=True, default='pending approval')
    reason = db.Column(db.String(256))
    voided = db.Column(db.Boolean, default=False)
    payment_status = db.Column(db.Enum("not paid","fully paid","partially paid","over paid", name="paid_status"), nullable=False, default="not_paid")
    bank_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"))

    balances = db.relationship("SupplierBalanceModel", back_populates="payment")
    account = db.relationship("AccountModel", back_populates="payment_account")
    invoice = db.relationship("InvoiceModel", back_populates="payments")
    accounting = db.relationship("SupplierPayAccountingModel", back_populates="payments", lazy="dynamic", cascade="all, delete-orphan")

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


    def approve_payment(self):
        self.approval_status = "approved"
        self.save_to_db()

    def reject_payment(self):
        self.approval_status = 'rejected'
        self.save_to_db()

