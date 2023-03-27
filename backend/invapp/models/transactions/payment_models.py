import uuid
from sqlalchemy.dialects.postgresql import UUID
from invapp.db import db
from datetime import datetime

class PaymentModel(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    payment_description = db.Column(db.String(256))
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default="KES")
    date = db.Column(db.DateTime, default=datetime.utcnow())
    update_date = db.Column(db.DateTime)
    approved = db.Column(db.Boolean, default=False)
    payment_status = db.Column(db.Enum("not_paid","fully_paid","partially_paid","over_paid", name="payment_status"), nullable=False, default="not_paid")
    pay_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"), nullable=False)

    purchase = db.relationship("PurchaseModel", back_populates="payments")
    accounting = db.relationship("SupplierPayAccountingModel", back_populates="payments", lazy="dynamic")

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


    def approve_payment(self):
        self.approved = True
        self.save_to_db()

