import datetime

from marshmallow import Schema, fields

from .supplierschema import PlainSupplierSchema, SupplierSchema
from .itemschema import PlainItemSchema
from ..models import ItemModel

class Invoice(Schema):
 id = fields.Int(required=True)
 supplier = fields.Nested(SupplierSchema(), dump_only=True)
 invoice_number = fields.String()
 amount = fields.Float(dump_only=True,required=True)
 matched_to_lines = fields.String(required=True, dump_only=True)

class ItemSchema(Schema):
 item_id = fields.Int(required=True)
 buying_price = fields.Float(required=True)
 quantity = fields.Int(required=True)
 description = fields.String()

class PlainPurchasingSchema(Schema):

 id = fields.Int(dump_only=True, required=True)
 item_cost = fields.Float(dump_only=True, required=True)
 items_list = fields.List(fields.Nested(ItemSchema()))
 invoice_id = fields.Int(required=True)


class PurchasingSchema(PlainPurchasingSchema):
 items = fields.Nested(PlainItemSchema(), dump_only=True)
 invoice = fields.Nested(Invoice(), dump_only=True)

class PurchaseUpdateSchema(Schema):
 pass
