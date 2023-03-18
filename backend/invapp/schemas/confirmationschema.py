from marshmallow import Schema, fields
from invapp.schemas.userschema import UserSchema

class ConfirmationSchema(Schema):
    user = fields.Nested(UserSchema(), dump_only=True)
    user_id = fields.Integer(required=True)
    expired_at = fields.Integer(dump_only=True, required=True)
    confirmed = fields.Boolean(dump_only=True, required=True)
    id = fields.String(dump_only=True, required=True)