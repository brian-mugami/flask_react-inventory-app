from ..db import db
from datetime import datetime


class CustomerModel(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(80), nullable=False, index=True, unique=True)
    customer_number = db.Column(db.Integer, db.Sequence(__tablename__ + "_id_seq", start= 2000,increment=1), index=True, unique=True)
    customer_contact = db.Column(db.String(80), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey("customer_account.id"), nullable=False, unique=True)
    date_unarchived = db.Column(db.DateTime)

    account = db.relationship("CustomerAccountModel", back_populates="customer")

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

class CustomerAccountModel(db.Model):
    __tablename__ = "customer_account"
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), nullable=False, unique=True)
    account_description = db.Column(db.String(256))
    account_number = db.Column(db.Integer, nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    date_unarchived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)

    customer = db.relationship("CustomerModel", back_populates="account",passive_deletes=True)

    def deactivate_account(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

        db.session.commit(self)

    def activate_account(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()

        db.session.commit(self)
