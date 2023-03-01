import os.path
from werkzeug.utils import secure_filename
from flask_smorest.fields import Upload
from marshmallow import Schema

class ImageSchema(Schema):
    file_1 = Upload()