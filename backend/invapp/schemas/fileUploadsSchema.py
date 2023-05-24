from marshmallow import Schema, fields
from flask_smorest import fields as smorest_fields

class FileUploadSchema(Schema):
    file = smorest_fields.Upload(required=True)