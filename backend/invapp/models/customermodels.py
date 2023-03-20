from ..db import db
from datetime import datetime


class CustomerModel(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(80), nullable=False, index=True, unique=True)
    customer_number = db.Column(db.Integer, db.Sequence("customers_id_seq", start= 2000,increment=1))
    customer_contact = db.Column(db.String(80), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)

    #payment_type = db.Column(db.Integer, db.ForeignKey("payment_types.id"), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete='SET DEFAULT'), server_default='1',nullable=False, unique=True)
    date_unarchived = db.Column(db.DateTime)

    account = db.relationship("AccountModel", back_populates="customer")

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


