import datetime
from marshmallow import Schema, fields, validate
from invapp.schemas.itemschema import PlainItemSchema
from invapp.schemas.paymentsschema import PayAccountSchema

class SupplierBalanceSchema(Schema):
    date = fields.Date()
    balance = fields.Float()
    paid = fields.Float()

class InvoiceSupplierSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    supplier_name = fields.String()

class InvoicePaymentSchema(Schema):
    approved = fields.Boolean()
    amount = fields.Float()
    payment_status = fields.String()
    payment_description = fields.String()

class Purchase_items(Schema):
    id = fields.Integer()
    item_quantity = fields.Integer()
    buying_price = fields.Float()
    item_cost = fields.Float()
    item_id = fields.Int()
    lines_cost = fields.Float()
    item = fields.Nested(PlainItemSchema(), dump_only=True)

class ExpenseAccountSchema(Schema):
    account_name = fields.String()
    account_number = fields.String()

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
    update_date = fields.Date()
    supplier_name = fields.String(required=True)
    expense_account_name = fields.String()
    expense_account_id = fields.Int(dump_only=True)

class InvoiceSchema(BaseInvoiceSchema):
    message = fields.Str()
    supplier = fields.Nested(InvoiceSupplierSchema(), dump_only=True)
    purchase_items = fields.Nested(Purchase_items(), many=True)
    supplier_balance = fields.Nested(SupplierBalanceSchema(),many=True ,dump_only=True)
    payments = fields.Nested(InvoicePaymentSchema(), many=True, dump_only=True)
    expense_account = fields.Nested(ExpenseAccountSchema(), dump_only=True)

class InvoiceUpdateSchema(Schema):
    purchase_type = fields.String(validate=validate.OneOf(["cash", "credit"]))
    destination_type = fields.String(validate=validate.OneOf(["expense", "stores"]))
    invoice_number = fields.String(validate=validate.Length(max=256))
    description = fields.String(validate=validate.Length(max=256))
    currency = fields.String(validate=validate.Length(max=10))
    amount = fields.Float()
    supplier_name = fields.String()
    expense_account_name = fields.String()

class InvoicePaymentSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    transaction_number = fields.UUID(required=True, dump_only=True)
    payment_description = fields.String()
    amount = fields.Float(required=True)
    currency = fields.String(required=True)
    date = fields.Date(dump_only=True)
    payment_status = fields.String(dump_only=True, required=True)
    update_date = fields.Date()
    bank_account_id = fields.Int(required=True, dump_only=True)
    bank_account = fields.String(required=True)
    approved = fields.Boolean(required=True, dump_only=True)

    invoice = fields.Nested(InvoiceSchema(), dump_only=True)
    account = fields.Nested(PayAccountSchema(), dump_only=True)

class SearchInvoiceToPaySchema(Schema):
    supplier_name = fields.String()
    date = fields.Date()

class InvoiceVoidSchema(Schema):
    voided = fields.Boolean(required=True)
    reason = fields.String(required=True)
