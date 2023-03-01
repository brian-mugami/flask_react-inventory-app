from marshmallow import fields,Schema

class SupplierAccountSchema(Schema):
    id = fields.String(required=True, dump_only=True)
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer()
    is_active = fields.Boolean(required=True, dump_only=True)
    date_created = fields.DateTime()
    date_archived = fields.DateTime()
    date_unarchived = fields.DateTime()
    is_archived = fields.Boolean(required=True, dump_only=True)

class SupplierSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    supplier_name = fields.String(required=True)
    supplier_number = fields.Int(required=True, dump_only=True)
    supplier_site = fields.String()
    supplier_contact = fields.String()
    is_active = fields.Boolean()
    is_archived = fields.Boolean()
    date_registered = fields.DateTime()
    date_archived = fields.DateTime()
    account_id = fields.Integer(required=True)
    account = fields.Nested(SupplierAccountSchema(), dump_only=True)

class SupplierAccountUpdateSchema(Schema):
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)
