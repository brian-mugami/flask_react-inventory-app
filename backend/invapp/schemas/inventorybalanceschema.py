from marshmallow import Schema, fields
from ..schemas import purchasingschema
from .itemschema import ItemSchema

class PlainInvBalanceSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    quantity = fields.String(required=True)
    cost = fields.Float(required=True)
    item_id = fields.Int(required=True)
    purchase_id = fields.Int()

class InvBalanceSchema(PlainInvBalanceSchema):
    date = fields.Date(required=True, dump_only=True)
    update_date = fields.Date()
    item = fields.Nested(ItemSchema(), dump_only=True)
    purchases = fields.Nested(purchasingschema.PlainPurchasingSchema(), dump_only=True)
    #accounting = fields.Nested()