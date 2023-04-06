import datetime

from marshmallow import fields, Schema, validate
from flask_smorest.pagination import PaginationParameters

class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    customer_name = fields.Str()

class ReceiptSchema(Schema):
    id = fields.Int(dump_only=True)
    transaction_number = fields.UUID(dump_only=True)
    receipt_number = fields.Int(dump_only=True)
    description = fields.Str()
    currency = fields.Str(required=True)
    date = fields.Date(required=True, default=datetime.datetime.utcnow())
    update_date = fields.DateTime(dump_only=True)
    amount = fields.Float(dump_only=True)
    sale_type = fields.Str(validate=validate.OneOf(["cash", "credit"]))
    accounted_status = fields.String(validate=validate.OneOf(["fully_accounted", "partially_accounted", "not_accounted"]))
    status = fields.String(validate=validate.OneOf(["fully paid", "partially paid", "not paid", "over paid"]))
    customer_id = fields.Int(required=True, dump_only=True)
    customer_name = fields.String(required=True)
    customer = fields.Nested(CustomerSchema(), dump_only=True)

