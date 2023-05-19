from marshmallow import fields,Schema

class AccountSchema(Schema):
    id = fields.String(required=True, dump_only=True)
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)
    account_type = fields.String()
    account_category = fields.String(required=True, dump_only=True)
    is_active = fields.Boolean(required=True, dump_only=True)
    date_created = fields.Date()
    date_archived = fields.Date()
    date_unarchived = fields.Date()
    is_archived = fields.Boolean(required=True, dump_only=True)

class AccountUpdateSchema(Schema):
    account_type = fields.String()
    account_name = fields.String()
    account_description = fields.String()
    account_number = fields.Integer()