from marshmallow import Schema, fields

from .supplierschema import SupplierSchema
from .itemschema import PlainItemSchema

class Invoice(Schema):
 id = fields.Int(required=True)
 supplier = fields.Nested(SupplierSchema(), dump_only=True)
 invoice_number = fields.String()
 amount = fields.Float(dump_only=True,required=True)
 matched_to_lines = fields.String(required=True, dump_only=True)

class PurchaseItemSchema(Schema):
 item_id = fields.Int(required=True, dump_only=True)
 item_name = fields.String(required=True)
 buying_price = fields.Float(required=True)
 item_quantity = fields.Int(required=True)
 item_cost = fields.Float(dump_only=True, required=True)
 description = fields.String()

class PlainPurchasingSchema(Schema):
 id = fields.Int(dump_only=True, required=True)
 items_list = fields.List(fields.Nested(PurchaseItemSchema(), required=True))
 invoice_id = fields.Int(required=True)
 line_cost = fields.Float(required=True,dump_only=True)

class PurchasingSchema(PlainPurchasingSchema):
 items = fields.Nested(PlainItemSchema(), dump_only=True)
 invoice = fields.Nested(Invoice(), dump_only=True)

class PurchaseUpdateSchema(Schema):
 item_id = fields.Int()
 buying_price = fields.Float()
 quantity = fields.Int()
 description = fields.String()
 item_cost = fields.Float(dump_only=True, required=True)


