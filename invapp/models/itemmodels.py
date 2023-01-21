from ..db import db
from datetime import datetime, timedelta

class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    item_image = db.Column(db.String(50), nullable=False, default="item.png")
    item_name = db.Column(db.String(80), nullable=False, index=True)
    item_number = db.Column(db.Integer, db.Sequence('seq_item_number', start=4000, increment=2))
    item_weight = db.Column(db.Float, default=0.00)
    item_volume = db.Column(db.Float, default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)
    date_unarchived = db.Column(db.DateTime)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False, default=1.00)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete='SET NULL'), nullable=True)

    category = db.relationship("CategoryModel", back_populates="items", lazy="subquery")
    lot = db.relationship("LotModel", back_populates="items", secondary="item_lots")

    def deactivate_item(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

        db.session.commit(self)

    def activate_item(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()
        db.session.commit(self)

class ItemAccountModel(db.Model):
    __tablename__ = "item_account"
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), nullable=False, unique=True)
    account_description = db.Column(db.String(256))
    account_number = db.Column(db.Integer, nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)
    date_unarchived = db.Column(db.DateTime)

    category = db.relationship("CategoryModel", back_populates="account", passive_deletes=True)

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

class LotModel(db.Model):
    __tablename__ = "lots"

    id = db.Column(db.Integer, primary_key=True)
    batch = db.Column(db.String(50), nullable=False, unique=True)
    lot = db.Column(db.String(50), nullable=False, unique=True)
    expiry_date = db.Column(db.DateTime, nullable=False, default= datetime.utcnow()+timedelta(days=256))
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_unarchived = db.Column(db.DateTime)
    date_archived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)

    items = db.relationship("ItemModel", back_populates="lot", secondary="item_lots")

    def deactivate_lot(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

        db.session.commit(self)

    def activate_lot(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()
        db.session.commit(self)

class CategoryModel(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)
    date_unarchived = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey("item_account.id"), nullable=False)

    items = db.relationship("ItemModel", back_populates="category", lazy="dynamic", cascade="all, delete")
    account = db.relationship("ItemAccountModel", back_populates="category")

    def deactivate_category(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

        db.session.commit(self)

    def activate_category(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()
        db.session.commit(self)

class ItemLotModel(db.Model):
    __tablename__ = "item_lots"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey("lots.id"), nullable=False)

