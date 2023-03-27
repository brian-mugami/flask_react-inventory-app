import uuid
from time import time
from invapp.db import db
from datetime import datetime
from flask import request, url_for
from invapp.libs.send_emails import Mailgun

CONFIRMTIMEDELTA = 3600

class UserModel (db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_archived = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())
    date_archived = db.Column(db.DateTime)
    date_unarchived = db.Column(db.DateTime)

    confirmation = db.relationship("ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def most_recent_confirmation(self):
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def make_inactive(self):
        self.is_active = False
        self.is_archived = True
        self.date_archived = datetime.utcnow()

        db.session.commit()

    def make_admin(self):
        self.is_admin = True
        db.session.commit()

    def activate(self):
        self.is_active = True
        self.is_archived = False
        self.date_archived = None
        self.date_unarchived = datetime.utcnow()
        db.session.commit()

    @classmethod
    def find_user_by_id(cls, _id: int):
        return cls.query.get_or_404(_id)

    @classmethod
    def find_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def send_confirmation_email(self):
        subject = "Registration Confirmation"
        link = request.url_root[:-1] + url_for("Confirmation.Confirmation", confirmation_id=self.most_recent_confirmation.id)
        text = f"Click here to confirm your registration: {link}"
        html = f"<html> Please click the link to confirm your registration: <a href={link}> Link </a> </html>"

        Mailgun.send_email([self.email], subject, text, html)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class ConfirmationModel(db.Model):
    __tablename__ = "confirmations"
    id = db.Column(db.String(50), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel",overlaps="confirmation")

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid.uuid4().hex
        self.expire_at = int(time()) + CONFIRMTIMEDELTA

    @classmethod
    def find_by_id(cls, _id:str):
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self):
        return time() > self.expire_at

    def force_to_expire(self):
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()