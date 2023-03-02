from flask import jsonify

from ..db import db
from ..models.itemmodels import CategoryModel,ItemModel,ItemAccountModel, LotModel
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from ..schemas.itemschema import LotSchema, CategorySchema, ItemSchema, PlainCategoryAccountSchema, CategoryAccountUpdateSchema, PlainCategorySchema

blp = Blueprint("Items", __name__, description="Actions on items")


@blp.route("/category/account")
class Categoryaccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainCategoryAccountSchema)
    @blp.response(201, PlainCategoryAccountSchema)
    def post(self, data):
        account = ItemAccountModel.query.filter_by(account_name=data["account_name"]).first()
        if account:
            abort(409, message="Account already exists")

        account = ItemAccountModel(account_name= data["account_name"],account_number=data["account_number"],
                                   account_description= data["account_description"])

        db.session.add(account)
        db.session.commit()
        return account
    @jwt_required(fresh=False)
    @blp.response(200, PlainCategoryAccountSchema(many=True))
    def get(self):
        accounts = ItemAccountModel.query.all()
        return accounts

@blp.route("/category/account/<int:id>")
class CategoryaccountView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, PlainCategoryAccountSchema)
    def delete(self, id):
        account = ItemAccountModel.query.get_or_404(id)
        db.session.delete(account)
        db.session.commit()

        return account

    @jwt_required(fresh=True)
    @blp.arguments(CategoryAccountUpdateSchema)
    def patch(self, data, id):
        account = ItemAccountModel.query.get_or_404(id)
        account.account_name = data["account_name"]
        account.account_description = data["account_description"]
        account.account_number = data["account_number"]
        db.session.commit()
        return jsonify({"message": "account updated"}), 202

    @jwt_required(fresh=True)
    @blp.response(202, PlainCategoryAccountSchema)
    def get(self, id):
        account = ItemAccountModel.query.get_or_404(id)

        return account

@blp.route("/item/lot")
class Itemlot(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(LotSchema)
    @blp.response(201, LotSchema)
    def post(self, data):
        lot = LotModel.query.filter_by(lot=data["lot"]).first()
        if lot:
            abort(409, message="Lot already exists")

        lot = LotModel(lot= data["lot"],batch=data["batch"], expiry_date=data["expiry_date"])

        db.session.add(lot)
        db.session.commit()

        return lot

    @jwt_required(fresh=False)
    @blp.response(200, LotSchema(many=True))
    def get(self):
        lots = LotModel.query.all()
        return lots

@blp.route("/item/lot/<int:id>")
class ItemLotView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(204, LotSchema)
    def delete(self, id):
        lot = LotModel.query.get_or_404(id)
        db.session.delete(lot)
        db.session.commit()
        return jsonify({"msg": "deleted successfully"})

    @jwt_required(fresh=True)
    @blp.arguments(LotSchema)
    @blp.response(202, LotSchema)
    def patch(self,data, id):
        lot = LotModel.query.get_or_404(id)
        lot.lot = data["lot"]
        lot.batch = data["batch"]
        lot.expiry_date = data["expiry_date"]

        db.session.commit()

        return lot

    @jwt_required(fresh=True)
    @blp.response(200, LotSchema)
    def get(self, id):
        lot = LotModel.query.get_or_404(id)
        return lot

@blp.route("/item/category")
class ItemCategory(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(CategorySchema)
    @blp.response(201, PlainCategorySchema)
    def post(self, data):
        category = CategoryModel.query.filter_by(name=data["name"]).first()
        if category:
            abort(409, message="Category already exists")
        account = ItemAccountModel.query.filter_by(account_name=data["account_name"]).first()
        if account is None:
            abort(404, message="Category Account does not exist")

        account_id = account.id
        category = CategoryModel(name= data["name"],account_id=account_id)

        db.session.add(category)
        db.session.commit()

        return category

    @jwt_required(fresh=False)
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        categories = CategoryModel.query.all()
        return categories

@blp.route("/item/category/<int:id>")
class CategoryView(MethodView):

    @jwt_required(fresh=True)
    @blp.response(202, CategorySchema)
    def delete(self, id):
        category = CategoryModel.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        return jsonify({"msg": "deleted successfully"})

    @jwt_required(fresh=True)
    @blp.response(202, CategorySchema)
    def get(self, id):
        category = CategoryModel.query.get_or_404(id)
        return category

    @jwt_required(fresh=True)
    @blp.arguments(CategorySchema)
    @blp.response(202, PlainCategorySchema)
    def patch(self, data, id):

        category = CategoryModel.query.get_or_404(id)
        category.name = data["name"]
        account = ItemAccountModel.query.filter_by(account_name=data["account_name"]).first()
        if account is None:
            abort(404, message="Category does not exist")
        account_id = account.id
        category.account_id = account_id

        db.session.commit()

@blp.route("/item")
class Item(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, data):
        item = ItemModel.query.filter_by(item_name=data["item_name"]).first()
        if item:
            abort(409, message="Item already exists")
        category = CategoryModel.query.filter_by(name=data["category_name"]).first()
        if category is None:
            abort(404, message="Category does not exist")
        category_id = category.id
        item = ItemModel(item_name= data["item_name"],price=data["price"], category_id=category_id, item_weight=data["item_weight"], item_volume=data["item_volume"], is_active=data["is_active"])
        db.session.add(item)
        db.session.commit()


        return item

    @jwt_required(fresh=False)
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        items = ItemModel.query.all()

        return items

@blp.route("/item/<int:id>")
class ItemView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, ItemSchema)
    def delete(self, id):
        item = ItemModel.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"msg": "deleted successfully"})

    @jwt_required(fresh=True)
    @blp.response(202, ItemSchema)
    def get(self, id):
        item = ItemModel.query.get_or_404(id)

        return item

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(202, ItemSchema)
    def patch(self, data, id):
        item = ItemModel.query.get_or_404(id)
        if item:
            item.price = data["price"]
            item.item_weight = data["item_weight"]
            item.item_volume = data["item_volume"]
            item.item_name = data["item_name"]
            item.is_active = data["is_active"]
            category = CategoryModel.query.filter_by(name=data["category_name"]).first()
            if category is None:
                abort(404, message="Category does not exist")

            category_id = category.id
            item.category_id = category_id

            db.session.commit()