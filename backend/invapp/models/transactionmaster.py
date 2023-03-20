from invapp.db import db
from datetime import datetime

class PayementTypeModel(db.Model):
    __tablename__ = "payment_types"

    id = db.Column(db.Integer, primary_key=True)
    payment_type_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)
    date_archived = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)

