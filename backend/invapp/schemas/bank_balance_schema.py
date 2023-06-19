from marshmallow import fields,Schema

from .accountsschema import AccountSchema
from .invoice_schema import InvoiceSchema
from .receiptschema import ReceiptSchema

class BankBalanceSearchSchema(Schema):
    name = fields.String(required=True)

class PlainBankBalanceSchema(Schema):
    id = fields.Integer(dump_only=True, required=True)
    date = fields.Date(dump_only=True)
    receipt_id = fields.Integer()
    invoice_id = fields.Integer()
    amount = fields.Float(required=True)
    currency = fields.String(required=True)
    bank_account_id = fields.Integer(required=True)
    update_date = fields.Date(dump_only=True)

class BankBalanceSchema(PlainBankBalanceSchema):
    account = fields.Nested(AccountSchema(), dump_only=True)
    invoice = fields.Nested(InvoiceSchema(), dump_only=True)
    receipt = fields.Nested(ReceiptSchema(), dump_only=True)

class BankBalanceUpdateSchema(Schema):
    amount = fields.Float()
    currency = fields.String()
    bank_account_id = fields.Integer()
    receipt_id = fields.Integer()
    invoice_id = fields.Integer()
    update_date = fields.Date(dump_only=True)