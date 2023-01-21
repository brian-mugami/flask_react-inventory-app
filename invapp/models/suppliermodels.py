from ..db import db
from datetime import datetime


class SupplierModel(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(80), nullable=False, index=True, unique=True)
    supplier_number = db.Column(db.Integer, db.Sequence('seq_sup_number', start=100, increment=5))
    supplier_site = db.Column(db.String(80), default="Main")
    supplier_contact = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    date_unarchived = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey("supplier_account.id"), nullable=False)

    account = db.relationship("SupplierAccountModel" ,back_populates="supplier")

    def deactivate_supplier(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

        db.session.commit(self)

    def activate_supplier(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()

        db.session.commit(self)

class SupplierAccountModel(db.Model):
    __tablename__ = "supplier_account"

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), nullable=False, unique=True)
    account_description = db.Column(db.String(256))
    account_number = db.Column(db.Integer, nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    date_unarchived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)

    supplier = db.relationship("SupplierModel", back_populates="account")

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