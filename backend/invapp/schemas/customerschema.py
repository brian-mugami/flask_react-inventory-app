from marshmallow import Schema,fields

class CustomerAccountSchema(Schema):
    id = fields.String(required=True, dump_only=True)
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)
    is_active = fields.Boolean(required=True, dump_only=True)
    date_created = fields.DateTime()
    date_archived = fields.DateTime()
    date_unarchived = fields.DateTime()
    is_archived = fields.Boolean(required=True, dump_only=True)

class CustomerSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    customer_name = fields.String(required=True)
    customer_number = fields.Integer(required=True, dump_only=True)
    customer_contact = fields.String()
    is_active = fields.Boolean()
    is_archived = fields.Boolean()
    date_registered = fields.Date()
    date_archived = fields.Date()
    account_id = fields.Integer(required=True, dump_only=True)
    date_unarchived = fields.Date()
    account_name = fields.String(required=True)

    account = fields.Nested(CustomerAccountSchema(), dump_only=True)

class CustomerAccountUpdateSchema(Schema):
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)