from marshmallow import fields,Schema
from .receiptschema import ReceiptSchema

class PlainCustomerPaymentSchema(Schema):

    id = fields.Integer(required=True, dump_only=True)
    transaction_number = fields.UUID(required=True, dump_only=True)
    amount = fields.Float(required=True)
    currency = fields.String(required=True)
    payment_description = fields.String()
    date = fields.Date(dump_only=True)
    payment_status = fields.String(dump_only=True, required=True)
    update_date = fields.Date()
    receipt_account = fields.String(required=True)
    receive_account_id = fields.Int(required=True, dump_only=True)
    receipt_id= fields.Int(required=True)
    approved = fields.Boolean(required=True, dump_only=True)

    receipt = fields.Nested(ReceiptSchema(), dump_only=True)

class PaymentUpdateSchema(Schema):
    amount = fields.Float()
    receive_account_id = fields.Int()
    receipt_id = fields.Int()
    approved = fields.Boolean()