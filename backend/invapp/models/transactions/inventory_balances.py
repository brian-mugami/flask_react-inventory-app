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
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id", ondelete='SET NULL'), nullable=True)
    sales_id = db.Column(db.Integer, db.ForeignKey("sales.id", ondelete='SET NULL'), nullable=True)

    item = db.relationship("ItemModel", back_populates="inventory_item")
    purchases = db.relationship("PurchaseModel", back_populates="inventory_item")
    accounting = db.relationship("PurchaseAccountingModel", back_populates="inventory_item")
    sales = db.relationship("SalesModel", back_populates="inventory_item")

    __table_args__ = (
        db.UniqueConstraint('item_id', 'purchase_id'),
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()