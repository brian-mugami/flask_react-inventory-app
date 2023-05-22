from backend.invapp.db import db
from datetime import datetime

class SupplierModel(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(80), nullable=False, index=True, unique=True)
    supplier_number = db.Column(db.Integer, db.Sequence("suppliers_id_seq", start=30000, increment=5), nullable=False)
    supplier_site = db.Column(db.String(80), default="Main")
    supplier_phone_no = db.Column(db.String(20), unique=True)
    supplier_email = db.Column(db.String(80), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    date_unarchived = db.Column(db.DateTime)
    payment_type = db.Column(db.Enum("cash", "credit", "none", name="payment_type_suppliers"))
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"),nullable=False, unique=True)

    account = db.relationship("AccountModel",back_populates="supplier")
    invoice = db.relationship("InvoiceModel", back_populates="supplier")
    balances = db.relationship("SupplierBalanceModel", back_populates="supplier")

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



