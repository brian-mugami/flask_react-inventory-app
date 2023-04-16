from marshmallow import fields, Schema, validate

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

class PaymentInvoiceSchema(Schema):
    amount = fields.Float()
    invoice_number = fields.String()
    accounted = fields.String(validate=validate.OneOf(["fully_accounted", "partially_accounted", "not_accounted"]))
    date = fields.Date()
    supplier = fields.Nested(InvoiceSupplierSchema(), dump_only=True)
    supplier_balance = fields.Nested(SupplierBalanceSchema(),many=True ,dump_only=True)
    payments = fields.Nested(InvoicePaymentSchema(), many=True, dump_only=True)

class PayAccountSchema(Schema):
    id = fields.Int()
    account_name = fields.Str()
    account_type =  fields.Str()
    account_number = fields.Int()
    account_category = fields.Str()

class PlainPaymentSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    transaction_number = fields.UUID(required=True, dump_only=True)
    payment_description = fields.String()
    amount = fields.Float(required=True)
    currency = fields.String(required=True)
    date = fields.Date(dump_only=True)
    payment_status = fields.String(dump_only=True, required=True)
    update_date = fields.Date(dump_only=True)
    bank_account_id = fields.Int(required=True)
    invoice_id = fields.Int(required=True)
    approved = fields.Boolean(required=True, dump_only=True)

    invoice = fields.Nested(PaymentInvoiceSchema(), dump_only=True)
    account = fields.Nested(PayAccountSchema(), dump_only=True)

class PaymentUpdateSchema(Schema):
    amount = fields.Float()
    bank_account_id = fields.Int()
    invoice_id = fields.Int()
    approved = fields.Boolean()
