import uuid
from sqlalchemy.dialects.postgresql import UUID
from invapp.db import db
from datetime import datetime
from sqlalchemy.types import Enum
import enum
class PaymentStatus(enum.Enum):
    fully_paid = "fully_paid"
    not_paid = "not_paid"
    partially_paid = "partially_paid"

class PaymentModel(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False, default="not_paid")

    pay_account_id = db.Column("accounts.id")
    invoice_id = db.Column(db.Integer, db.ForeignKey("purchases.id"))

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
