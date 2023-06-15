import traceback
import asyncio
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..db import db
import pandas as pd

from ..models import CategoryModel, ItemModel
from ..models import AccountModel
from ..schemas.fileUploadsSchema import FileUploadSchema

blp = Blueprint("Uploading", __name__, description="Uploads")


@blp.route("/category/account/upload")
class CategoryAccountUpload(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(FileUploadSchema, location="files")
    def post(self, data):
        file = data.get("file")
        allowed_extensions = ["xlsx"]
        extension = file.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            abort(400, message="Only excel files are allowed")
        excel_data = pd.read_excel(file, sheet_name="CATEGORY_ACCOUNT")
        for index, row in excel_data.iterrows():
            account = AccountModel(account_name=row["ACCOUNT_NAME"], account_number=row["ACCOUNT_NUMBER"],
                                   account_description=row["ACCOUNT_DESCRIPTION"], account_category="Item Account")
            account.save_to_db()
        try:
            return {"message": "Saved successfully"}, 200
        except IntegrityError as e:
            traceback.print_exc()
            abort(500,
                  message="Something went wrong when uploading, check on duplicates")
        print(f"{len(excel_data)} added successfully")


@blp.route("/category/upload")
class CategoryUpload(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(FileUploadSchema, location="files")
    def post(self, data):
        file = data.get("file")
        allowed_extensions = ["xlsx"]
        extension = file.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            abort(400, message="Only excel files are allowed")
        excel_data = pd.read_excel(file, sheet_name="CategoryForm")
        for index, row in excel_data.iterrows():
            account = AccountModel.query.filter_by(account_name=row["account"], account_category="Item Account").first()
            if not account:
                abort(404, message=f"{row['account']} is not an account found")
            category = CategoryModel(name=row['name'], account_id=account.id)
            category.save_to_db()
        try:
            return {"message": "Saved successfully"}, 200
        except IntegrityError as e:
            traceback.print_exc()
            abort(500, message=f"Something went wrong when uploading, check on duplicates")


@blp.route("/item/upload")
class ItemUpload(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(FileUploadSchema, location="files")
    def post(self, data):
        file = data.get("file")
        allowed_extensions = ["xlsx"]
        extension = file.filename.rsplit('.', 1)[-1].lower()
        if extension not in allowed_extensions:
            abort(400, message="Only excel files are allowed")

        excel_data = pd.read_excel(file, sheet_name="ItemUploadForm")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        save_items_coroutine = partial(self.save_items, excel_data)
        result = loop.run_until_complete(save_items_coroutine())

        loop.close()

        return {"message": result}, 200

    async def save_items(self, excel_data):
        executor = ThreadPoolExecutor()
        tasks = []
        for index, row in excel_data.iterrows():
            category = CategoryModel.query.filter_by(name=row['item_category']).first()
            if not category:
                abort(400, message=f"{row['item_category']} does not exist")

            item = ItemModel(item_name=row["item_name"], price=row["price"], category_id=category.id,
                             item_unit=row["item_unit"], unit_type=row["unit_type"])
            task = asyncio.get_event_loop().run_in_executor(executor, item.save_to_db())
            tasks.append(task)

        try:
            await asyncio.gather(*tasks)
            return jsonify ({"Saved":" successfully"}), 200
        except Exception as e:
            return f"Error occurred: {str(e)}"
