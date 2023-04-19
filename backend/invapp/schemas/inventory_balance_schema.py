from marshmallow import Schema, fields

from invapp.schemas.salesschema import Receipt

class ItemSchema(Schema):
    item_name = fields.String()

class InvoiceSchema(Schema):
    invoice_number = fields.String()
    amount = fields.Float()

class PlainInventoryBalanceSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    quantity = fields.Int(required=True)
    unit_cost = fields.Float()
    date = fields.Date(dump_only=True, required=True)
    item_id = fields.Int(required=True, dump_only=True)
    item_name = fields.String(required=True)
    receipt_id = fields.Int()
    invoice_id = fields.Int()

class InventoryBalanceSchema(PlainInventoryBalanceSchema):
    item = fields.Nested(ItemSchema(), dump_only=True)
    invoice = fields.Nested(InvoiceSchema(), dump_only=True)
    receipt = fields.Nested(Receipt(), dump_only=True)

class BalanceSearchSchema(Schema):
    item_name = fields.String(required=True)



