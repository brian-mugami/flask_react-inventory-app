from marshmallow import Schema,fields
from .accountsschema import AccountSchema

class BaseCustomerSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    customer_name = fields.String(required=True)
    customer_number = fields.Integer(required=True, dump_only=True)
    customer_phone_no = fields.String()
    customer_email = fields.Email()
    customer_site = fields.String()
    customer_bill_to_site = fields.String()


class CustomerSchema(BaseCustomerSchema):
    is_active = fields.Boolean()
    is_archived = fields.Boolean()
    date_registered = fields.Date()
    date_archived = fields.Date()
    payment_type = fields.String(required=True)
    account_id = fields.Integer(required=True, dump_only=True)
    date_unarchived = fields.Date()
    account_name = fields.String(required=True)

    account = fields.Nested(AccountSchema(), dump_only=True)

class CustomerUpdateSchema(Schema):
    customer_phone_no = fields.String()
    customer_email = fields.Email()
    payment_type = fields.String()
    customer_name = fields.String()
    account_id = fields.Integer()
    is_active = fields.Boolean()
    customer_site = fields.String()
    customer_bill_to_site = fields.String()


class CustomerAccountUpdateSchema(Schema):
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)

