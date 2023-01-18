from ..db import db
from datetime import datetime


class CustomerModel(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(80), nullable=False, index=True, unique=True)
    customer_number = db.Column(db.Integer,db.Sequence('seq_reg_id', start=2001, increment=1), index=True)
    customer_contact = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey("customer_account.id"), nullable=False)

    account = db.relationship("CustomerAccountModel", back_populates="customer")

class CustomerAccountModel(db.Model):
    __tablename__ = "customer_account"
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), nullable=False, unique=True)
    account_description = db.Column(db.String(256))
    account_number = db.Column(db.Integer, nullable=False, unique=True)

    customer = db.relationship("CustomerModel", back_populates="customer_account",passive_deletes=True)
