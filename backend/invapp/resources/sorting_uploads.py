from flask_smorest import Blueprint,abort
from flask.views import MethodView
from ..db import db
import pandas as pd

from ..models import CategoryModel
from ..schemas.fileUploadsSchema import FileUploadSchema

blp = Blueprint("Uploading", __name__, description="Uploads")

@blp.route("/category/upload")
class CategoryUpload(MethodView):
    @blp.arguments(FileUploadSchema)
    def post(self, data):
        file = data.get("file")
        allowed_extensions = ["xlsx"]
        extension = file.filename.rsplit('.', 1)[-1].lower()

        if extension not in allowed_extensions:
            abort(400, message="Only excel files are allowed")
        excel_data = pd.read_excel(file)
        for index, row in data.iterrows():
            try:
                category = CategoryModel()
                pass
            except:
                pass



