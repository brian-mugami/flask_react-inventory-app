from invapp.db import db
from datetime import datetime

class AccountModel(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), nullable=False, unique=True)
    account_description = db.Column(db.String(256))
    account_type = db.Column(db.Enum("cash", "credit","none" ,name="account_types"), default="none")
    account_number = db.Column(db.String(100), nullable=False)
    account_category = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    date_unarchived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('account_name', "account_number", 'account_category', name="account_unique_check"),
    )

    category = db.relationship("CategoryModel", back_populates="account", passive_deletes=True, lazy="dynamic")
    supplier = db.relationship("SupplierModel", back_populates="account", lazy="dynamic", passive_deletes=True)
    customer = db.relationship("CustomerModel", back_populates="account", passive_deletes=True, lazy="dynamic")
    payment_account = db.relationship("PaymentModel", back_populates="account", lazy="dynamic")

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

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()