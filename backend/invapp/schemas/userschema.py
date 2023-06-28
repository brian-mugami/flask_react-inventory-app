from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Integer(Required=True,dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    password1 = fields.String(required=True, load_only=True)
    password2 = fields.String(required=True, load_only=True)
    is_active = fields.Boolean(required=False)
    is_admin = fields.Boolean(required=True, dump_only=True)
    is_archived = fields.Boolean(required=False)
    date_registered = fields.Date(required=False)
    date_archived = fields.Date(required=False)
    last_login = fields.DateTime(required=False)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class UserUpdateSchema(Schema):
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    password = fields.String()
    is_active = fields.Boolean()
    is_archived = fields.Boolean()
    date_registered = fields.Date()
    date_archived = fields.Date()

class PaswordChangeSchema(Schema):
    email = fields.Email(required=True)
    password1 = fields.String()
    password2 = fields.String()

