from marshmallow import Schema, fields

class PlainItemSchema(Schema):
    id = fields.Integer(required=True, dump_only=True)
    item_image = fields.String()
    item_name = fields.String(required=True)
    item_number = fields.Integer(required=True, dump_only=True)
    item_weight = fields.Float()
    item_volume = fields.Float()
    is_active = fields.Boolean()
    date_created = fields.DateTime()
    date_archived = fields.DateTime()
    is_archived = fields.Boolean()
    price = fields.Float(required=True)
    category_id = fields.Integer(required=True, load_only=True)

class PlainItemAccountSchema(Schema):
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
    expiry_date = fields.DateTime()
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
    account_id = fields.Integer(required=True, load_only=True)
    account = fields.Nested(PlainItemAccountSchema(), dump_only=True)

class ItemAccountSchema(PlainItemAccountSchema):
    category = fields.Nested(PlainItemAccountSchema(), dump_only = True)
class CategorySchema(PlainCategorySchema):
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))

class ItemSchema(PlainItemSchema):
    category = fields.Nested(PlainCategorySchema(), dump_only=True)
    lot = fields.List(fields.Nested(PlainLotSchema(), dump_only=True))