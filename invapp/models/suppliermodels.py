from ..db import db
from datetime import datetime


class SupplierModel(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(80), nullable=False, index=True, unique=True)
    supplier_number = db.Column(db.Integer, db.Sequence('seq_reg_id', start=3001, increment=1), index=True)
    supplier_site = db.Column(db.String(80), default="Main")
    supplier_contact = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey("supplier_account.id"), nullable=False)

    account = db.relationship("SupplierAccountModel" ,back_populates="supplier")

class SupplierAccountModel(db.Model):
    __tablename__ = "supplier_account"

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), nullable=False, unique=True)
    account_description = db.Column(db.String(256))
    account_number = db.Column(db.Integer, nullable=False, unique=True)

    supplier = db.relationship("SupplierModel", back_populates="account")

