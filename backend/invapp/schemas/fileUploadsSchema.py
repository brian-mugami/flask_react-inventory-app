from marshmallow import Schema
from flask_smorest.fields import Upload
class FileUploadSchema(Schema):
    file = Upload(required=True)
