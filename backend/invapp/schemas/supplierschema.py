from marshmallow import fields,Schema


class SupplierAccountSchema(Schema):
    id = fields.String(required=True, dump_only=True)
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)
    account_category = fields.String(dump_default="Supplier Account")
    is_active = fields.Boolean(required=True, dump_only=True)
    date_created = fields.Date()
    date_archived = fields.Date()
    date_unarchived = fields.Date()
    is_archived = fields.Boolean(required=True, dump_only=True)

class PlainSupplierSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    supplier_name = fields.String(required=True)
    supplier_number = fields.Int(required=True, dump_only=True)
    supplier_site = fields.String()
    supplier_phone_no = fields.String()
    supplier_email = fields.String()

class SupplierSchema(PlainSupplierSchema):

    is_active = fields.Boolean()
    is_archived = fields.Boolean()
    date_registered = fields.Date()
    date_archived = fields.Date()
    payment_type = fields.String()
    account_id = fields.Integer(required=True, dump_only=True)
    account_name = fields.String(required=True)
    account = fields.Nested(SupplierAccountSchema(), dump_only=True)


#class SupplierDetailedSchema(PlainSupplierSchema):
 #   from .purchasingschema import PlainPurchasingSchema
  #  purchases = fields.List(fields.Nested(PlainPurchasingSchema(), dump_only=True))

class SupplierAccountUpdateSchema(Schema):
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)

class SupplierCountSchema(Schema):
    active_suppliers = fields.Integer(required=True, dump_only=True)