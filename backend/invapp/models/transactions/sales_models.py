from invapp.db import db

class SalesModel(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float(precision=4), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipts.id"), nullable=False)
    item_cost = db.Column(db.Float(precision=4), nullable=False)

    receipt = db.relationship("ReceiptModel", back_populates="sale_items")
    item = db.relationship("ItemModel", back_populates="sales")


    __table_args__ = (
        db.UniqueConstraint('item_id', 'receipt_id', name="sales_lines_constraint"),
    )

    @classmethod
    def find_by_id(cls,_id: int):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_receipt_number(cls, num):
        return cls.query.filter_by(receipt_number=num).first()

    @property
    def amount(self):
        return self.quantity * self.selling_price

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()