from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Integer(Required=True,dump_only=True)
    email = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    password1 = fields.String(required=True, load_only=True)
    password2 = fields.String(required=True, load_only=True)
    is_active = fields.Boolean(required=False)
    is_archived = fields.Boolean(required=False)
    date_registered = fields.Date(required=False)
    date_archived = fields.Date(required=False)

class LoginSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class UserUpdateSchema(Schema):
    email = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    password1 = fields.String()
    password2 = fields.String()
    is_active = fields.Boolean()
    is_archived = fields.Boolean()
    date_registered = fields.Date()
    date_archived = fields.Date()