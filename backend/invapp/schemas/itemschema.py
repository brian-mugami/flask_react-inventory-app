from marshmallow import Schema, fields
from datetime import datetime, timedelta


class PlainItemSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    item_image = fields.String()
    item_name = fields.String(required=True)
    item_number = fields.Integer(required=True, dump_only=True)
    item_weight = fields.Float()
    item_volume = fields.Float()
    is_active = fields.Boolean()
    date_created = fields.Date()
    date_archived = fields.Date()
    is_archived = fields.Boolean()
    price = fields.Float(required=True)
    category_id = fields.Integer(required=True, dump_only=True)
    category_name = fields.String(required=True)

class PlainCategoryAccountSchema(Schema):
    id = fields.String(required=True, dump_only=True)
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)
    is_active = fields.Boolean(required=True, dump_only=True)
    date_created = fields.DateTime()
    date_archived = fields.DateTime()
    date_unarchived = fields.DateTime()
    is_archived = fields.Boolean(required=True, dump_only=True)
class PlainLotSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    batch = fields.String(required=True)
    lot = fields.String(required=True)
    expiry_date = fields.Date(required=True, default=datetime.now() + timedelta(days=256))
    is_active = fields.Boolean()
    date_created = fields.DateTime()
    date_archived = fields.DateTime()
    is_archived = fields.Boolean()

class LotSchema(PlainLotSchema):
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))

class PlainCategorySchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    name = fields.String(required=True)
    is_active = fields.Boolean()
    date_created = fields.DateTime()
    date_archived = fields.DateTime()
    is_archived = fields.Boolean()
    account_name = fields.String(required=True)
    account_id = fields.Integer(required=True, dump_only=True)
    account = fields.Nested(PlainCategoryAccountSchema(), dump_only=True)

class ItemAccountSchema(PlainCategoryAccountSchema):
    category = fields.Nested(PlainCategoryAccountSchema(), dump_only = True)
class CategorySchema(PlainCategorySchema):
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))

class ItemSchema(PlainItemSchema):
    category = fields.Nested(PlainCategorySchema(), dump_only=True)
    lot = fields.List(fields.Nested(PlainLotSchema(), dump_only=True))

class CategoryAccountUpdateSchema(Schema):
    account_name = fields.String(required=True)
    account_description = fields.String()
    account_number = fields.Integer(required=True)