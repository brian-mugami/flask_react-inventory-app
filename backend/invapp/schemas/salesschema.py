from marshmallow import fields,Schema
from .itemschema import BaseItemSchema
from .customerschema import BaseCustomerSchema

import random

random_number = random.randint(10**9, 10**10 - 1)


class PlainSalesSchema(Schema):
    id = fields.Int(dump_only=True,required=True)
    receipt_number = fields.Int(required=True, dump_only=True)
    transaction_number = fields.UUID(required=True, dump_only=True)
    description = fields.String()
    quantity = fields.Int(required=True)
    selling_price = fields.Float(required=True)
    currency = fields.String(required=True)
    update_date = fields.Date()
    date_sold = fields.Date(required=True, dump_only=True)
    sale_type = fields.String(required=True)
    item_id = fields.Int(required=True)
    customer_id = fields.Int(required=True)

class SalesSchema(PlainSalesSchema):
    item = fields.Nested(BaseItemSchema(), dump_only=True)
    customer = fields.Nested(BaseCustomerSchema(), dump_only=True)