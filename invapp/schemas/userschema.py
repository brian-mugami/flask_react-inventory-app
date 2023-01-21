from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Integer(Required=True,dump_only=True)
    email = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    profile_image = fields.String()
    password = fields.String(required=True, load_only=True)
    is_active = fields.Boolean()
    is_archived = fields.Boolean()
    date_registered = fields.DateTime()
    date_archived = fields.DateTime()

class LoginSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)