import uuid
from sqlalchemy.dialects.postgresql import UUID
from invapp.db import db
from datetime import datetime

class SalesModel(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(UUID(as_uuid=True),index=True, unique=True, nullable=False,  default=uuid.uuid4)
    receipt_number = db.Column(db.Integer, db.Sequence("customers_id_seq", start=100, increment=5), nullable=False, index=True, unique=True)
    description = db.Column(db.String(256), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float(precision=4), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    update_date = db.Column(db.DateTime)
    date_sold = db.Column(db.DateTime, default=datetime.utcnow())
    sale_type = db.Column(db.Enum("cash", "credit", name="sales_types"), default="cash", nullable=False)

    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)

    inventory_item = db.relationship("InventoryBalancesModel", back_populates="sales", lazy="dynamic")
    item = db.relationship("ItemModel", back_populates="sales")
    customer = db.relationship("CustomerModel", back_populates="sales")
    accounting = db.relationship("SalesAccountingModel", back_populates="sales")
    customer_balance = db.relationship("CustomerBalanceModel", back_populates="sales")
    received = db.relationship("CustomerPaymentModel", back_populates="sales")

    __table_args__ = (
        db.UniqueConstraint('item_id', 'customer_id', 'receipt_number', name="sales_unique_constraint"),
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