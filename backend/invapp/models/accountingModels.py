import uuid

from invapp.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class IncomeAccountingModel(db.Model):
    __tablename__ = "income_balances"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    credit_amount = db.Column(db.Float,default=0.000)
    debit_amount = db.Column(db.Float,default=0.000)