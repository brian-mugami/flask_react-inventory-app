from marshmallow import fields,Schema
from .purchasingschema import PlainPurchasingSchema

class PayAccountSchema(Schema):
    id = fields.Int()
    account_name = fields.Str()
    account_type =  fields.Str()
    account_number = fields.Int()
    account_category = fields.Str()

class PlainPaymentSchema(Schema):

    id = fields.Integer(required=True, dump_only=True)
    transaction_number = fields.UUID(required=True, dump_only=True)
    amount = fields.Float(required=True)
    currency = fields.String(required=True)
    date = fields.Date(dump_only=True)
    payment_status = fields.String(dump_only=True, required=True)
    update_date = fields.Date()
    pay_account_id = fields.Int(required=True)
    invoice_id = fields.Int(required=True)
    approved = fields.Boolean(required=True, dump_only=True)

    invoice = fields.Nested(PlainPurchasingSchema(), dump_only=True)
    account = fields.Nested(PayAccountSchema(), dump_only=True)

class PaymentUpdateSchema(Schema):
    amount = fields.Float()
    pay_account_id = fields.Int()
    invoice_id = fields.Int()
    approved = fields.Boolean()
