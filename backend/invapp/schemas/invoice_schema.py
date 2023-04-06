import datetime
from marshmallow import Schema, fields, validate
from invapp.schemas.itemschema import PlainItemSchema

class InvoiceSupplierSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    supplier_name = fields.String()

class Purchase_items(Schema):
    item_quantity = fields.Integer()
    buying_price =  fields.Float()
    item_cost = fields.Float()
    item_id = fields.Int()
    items = fields.Nested(PlainItemSchema(), dump_only=True)

class BaseInvoiceSchema(Schema):
    id = fields.Integer(dump_only=True)
    transaction_number = fields.UUID(dump_only=True)
    invoice_number = fields.String(required=True, validate=validate.Length(max=256))
    description = fields.String(validate=validate.Length(max=256))
    currency = fields.String(required=True, validate=validate.Length(max=10))
    amount = fields.Float(required=True)
    accounted = fields.String(validate=validate.OneOf(["fully_accounted", "partially_accounted", "not_accounted"]))
    status = fields.String(validate=validate.OneOf(["fully paid", "partially paid", "not paid", "over paid"]))
    matched_to_lines = fields.String(validate=validate.OneOf(["matched", "unmatched", "partially matched"]), dump_only=True)
    date = fields.Date(required=True, default=datetime.datetime.utcnow())
    destination_type = fields.String(validate=validate.OneOf(["expense", "stores"]), required=True)
    purchase_type = fields.String(validate=validate.OneOf(["cash", "credit"]))
    update_date = fields.DateTime()
    supplier_name = fields.String(required=True)

class InvoiceSchema(BaseInvoiceSchema):
    supplier = fields.Nested(InvoiceSupplierSchema(), dump_only=True)
    purchase_items = fields.Nested(Purchase_items(), many=True)

class InvoiceApproveSchema(Schema):
    expense_type = fields.Str()