from invapp.db import db

class PurchaseModel(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=True)
    item_quantity = db.Column(db.Integer, nullable=False, default=0)
    buying_price = db.Column(db.Float(precision=4), nullable=False, default=0)
    item_cost = db.Column(db.Float, nullable=False, default=0)
    update_date = db.Column(db.DateTime)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"))

    items = db.relationship("ItemModel", back_populates="purchases")
    invoice = db.relationship("InvoiceModel", back_populates="purchase_items")

    inventory_item = db.relationship("InventoryBalancesModel", back_populates="purchases", lazy="dynamic")
    expense_item = db.relationship("ExpensesModel", back_populates="expenses", lazy="dynamic")
    accounting = db.relationship("PurchaseAccountingModel", back_populates="purchases", lazy="dynamic")
    payments = db.relationship("PaymentModel", back_populates="purchase", lazy="dynamic")
    supplier_balance = db.relationship("SupplierBalanceModel", back_populates="purchase", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint('item_id', 'invoice_id', name="purchase_unique_constraint"),
    )

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_invoice_number(cls, num):
        return cls.query.filter_by(invoice_number=num).first()

    @property
    def amount(self):
        return self.quantity * self.buying_price

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

