import datetime

from marshmallow import Schema, fields

from .supplierschema import PlainSupplierSchema
from .itemschema import PlainItemSchema
from ..models import ItemModel


class ItemSchema(Schema):
 id = fields.Int(required=True)
 buying_price = fields.Float(required=True)
 quantity = fields.Int(required=True)

class PlainPurchasingSchema(Schema):

 id = fields.Int(dump_only=True, required=True)
 description = fields.String()
 item_cost = fields.Float(dump_only=True, required=True)
 currency = fields.String(required=True)
 destination_type = fields.String(required=True)
 expense_type = fields.String()
 items = fields.Nested(ItemSchema(), many=True, required=True)


class PurchasingSchema(PlainPurchasingSchema):
 pass

class PurchaseUpdateSchema(Schema):
 invoice_number = fields.String()
 description = fields.String()
 quantity = fields.Integer()
 buying_price = fields.Float()
 currency = fields.String()
 date = fields.Date()
 supplier_id = fields.Int()
 item_ids = fields.List(fields.Integer())
 purchase_type = fields.String()
 update_date = fields.Date()
 destination_type = fields.String()
 expense_type = fields.String()
