from marshmallow import Schema, fields

from .supplierschema import PlainSupplierSchema
from .itemschema import PlainItemSchema

class PlainPurchasingSchema(Schema):

 id = fields.Int(dump_only=True, required=True)
 invoice_number = fields.String(required=True)
 transaction_number = fields.UUID(required=True, dump_only=True)
 description = fields.String()
 quantity = fields.Integer(required=True)
 buying_price = fields.Float(required=True)
 currency = fields.String(required=True)
 date_of_supply = fields.Date()
 supplier_id = fields.Int(required=True)
 item_id = fields.Int(required=True)
 purchase_type = fields.String(required=True)


class PurchasingSchema(PlainPurchasingSchema):
 supplier = fields.Nested(PlainSupplierSchema(), dump_only=True)
 items = fields.Nested(PlainItemSchema(), dump_only=True)

class PurchaseUpdateSchema(Schema):
 invoice_number = fields.String()
 description = fields.String()
 quantity = fields.Integer()
 buying_price = fields.Float()
 currency = fields.String()
 date_of_supply = fields.Date()
 supplier_id = fields.Int()
 item_id = fields.Int()
 purchase_type = fields.String()
 update_date = fields.Date()
