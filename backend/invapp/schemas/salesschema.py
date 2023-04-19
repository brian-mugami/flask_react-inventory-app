from marshmallow import fields,Schema
from .customerschema import BaseCustomerSchema

class Receipt(Schema):
    receipt_number = fields.Int()
    customer = fields.Nested(BaseCustomerSchema(), dump_only=True)

class ReceiptItemSchema(Schema):
    item_id = fields.Int(dump_only=True)
    selling_price = fields.Float(required=True)
    quantity = fields.Int(required=True)
    item_name = fields.String(required=True)

class PlainSalesSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    receipt_id = fields.Int(required=True)
    item_list = fields.List(fields.Nested(ReceiptItemSchema(), required=True))
    item_cost = fields.Float(required=True, dump_only=True)

class SalesSchema(PlainSalesSchema):
    receipt = fields.Nested(Receipt(), dump_only=True)

