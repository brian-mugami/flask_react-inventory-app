from marshmallow import Schema, fields

class InventoryBalanceSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    quantity = fields.Int(required=True)
    unit_cost = fields.Float(required=True)
    date = fields.Date(dump_only=True)
    item_id = fields.Int(required=True)
    receipt_id = fields.Int()
    invoice_id = fields.Int()
