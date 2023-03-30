import enum

from invapp.db import db
from datetime import datetime

class PaymentType(enum.Enum):
    cash = "cash"
    credit = "credit"

class CustomerModel(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(80), nullable=False, index=True, unique=True)
    customer_number = db.Column(db.Integer, db.Sequence("customers_id_seq", start= 2000,increment=1))
    customer_phone_no = db.Column(db.String(80), unique=True)
    customer_email = db.Column(db.String(80), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    payment_type = db.Column(db.Enum("cash","credit","none", name="payment_type"))
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"),nullable=False, unique=True)
    date_unarchived = db.Column(db.DateTime)

    account = db.relationship("AccountModel", back_populates="customer")
    sales = db.relationship("SalesModel", back_populates="customer")

    def deactivate_customer(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

        db.session.commit(self)

    def activate_customer(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()

        db.session.commit(self)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()




