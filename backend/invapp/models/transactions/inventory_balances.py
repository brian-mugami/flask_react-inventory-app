from invapp.db import db
from datetime import datetime

class InventoryBalancesModel(db.Model):
    __tablename__ = "inventory balances"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False, default=0.00)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    update_date = db.Column(db.DateTime)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id", ondelete='SET NULL'), nullable=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipts.id", ondelete='SET NULL'), nullable=True)

    item = db.relationship("ItemModel", back_populates="inventory_item")
    invoice = db.relationship("InvoiceModel", back_populates="inventory_item")
    receipt = db.relationship("ReceiptModel", back_populates="inventory_item")

    __table_args__ = (
        db.UniqueConstraint('item_id', 'invoice_id', 'receipt_id'),
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()