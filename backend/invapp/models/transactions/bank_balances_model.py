from datetime import datetime

from backend.invapp.db import db

class BankBalanceModel(db.Model):
    __tablename__ = "bank_balances"

    id = db.Column(db.Integer, primary_key = True)
    currency = db.Column(db.String(10), default="KES")
    amount = db.Column(db.Float(precision=2), nullable= False)
    bank_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipts.id"), nullable=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    update_date = db.Column(db.DateTime)

    account = db.relationship("AccountModel", back_populates="bank_balance")
    receipt = db.relationship("ReceiptModel", back_populates="bank_balance")
    invoice = db.relationship("InvoiceModel", back_populates="bank_balance")

    __table_args__ = (
        db.UniqueConstraint('receipt_id', "invoice_id", 'bank_account_id', name="bank_balance_constraint"),
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()