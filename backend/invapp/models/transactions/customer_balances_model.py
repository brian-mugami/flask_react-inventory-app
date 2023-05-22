from backend.invapp.db import db

class CustomerBalanceModel(db.Model):
    __tablename__ = "customer_balances"

    id = db.Column(db.Integer, primary_key = True)
    currency = db.Column(db.String(10), default="KES")
    receipt_amount = db.Column(db.Float, nullable=False, default=0.00)
    paid = db.Column(db.Float, nullable= True, default=0.00)
    balance = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipts.id"))


    customer = db.relationship("CustomerModel", back_populates="balances")
    receipt = db.relationship("ReceiptModel", back_populates="customer_balance")
    accounting = db.relationship("CustomerPayAccountingModel", back_populates="balance")

    __table_args__ = (
        db.UniqueConstraint('receipt_id', 'currency', "customer_id"),
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