from ..db import db
from datetime import datetime

class UserModel (db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(50), nullable=False, default="default.png")
    email = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    date_unarchived = db.Column(db.DateTime)

    def make_inactive(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

    def make_admin(self):
        self.is_admin = True

    def activate(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()