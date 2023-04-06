from invapp.db import db

class SupplierBalanceModel(db.Model):
    __tablename__ = "supplier balances"

    id = db.Column(db.Integer, primary_key = True)
    currency = db.Column(db.String(10), default="KES")
    invoice_amount = db.Column(db.Float, nullable=False, default=0.00)
    paid = db.Column(db.Float, nullable= True, default=0.00)
    balance = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime)

    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"))
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"))

    supplier = db.relationship("SupplierModel", back_populates="balances")
    invoice = db.relationship("InvoiceModel", back_populates="supplier_balance")
    accounting = db.relationship("SupplierPayAccountingModel", back_populates="balance")

    __table_args__ = (
        db.UniqueConstraint('supplier_id', 'currency', "invoice_id"),
    )

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()