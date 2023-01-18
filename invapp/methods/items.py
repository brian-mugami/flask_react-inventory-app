from ..db import db
from ..models.itemmodels import CategoryModel,ItemModel,ItemAccountModel, LotModel
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from ..schemas import  ItemAccountSchema, AccountSchema, LotSchema, CategorySchema, ItemSchema

blp = Blueprint("Items", __name__, description="Actions on items")


@blp.route("/item/account")
class Itemaccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ItemAccountSchema)
    @blp.response(201, AccountSchema)
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
    @blp.response(201, AccountSchema(many=True))
    def get(self):
        accounts = ItemAccountModel.query.all()
        return accounts

@blp.route("/item/lot")
class Itemlot(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(LotSchema)
    @blp.response(201, LotSchema)
    def post(self, data):
        lot = LotModel.query.filter_by(lot=data["lot"]).first()
        if lot:
            abort(409, message="Lot already exists")

        lot = LotModel(lot= data["lot"],batch=data["batch"])

        db.session.add(lot)
        db.session.commit()

        return lot

    @jwt_required(fresh=False)
    @blp.response(200, LotSchema(many=True))
    def get(self):
        lots = LotModel.query.all()
        return lots

@blp.route("/item/category")
class ItemCat(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(CategorySchema)
    @blp.response(201, CategorySchema)
    def post(self, data):
        category = CategoryModel.query.filter_by(name=data["name"]).first()
        if category:
            abort(409, message="Category already exists")

        category = CategoryModel(name= data["name"],account_id=data["account_id"])

        db.session.add(category)
        db.session.commit()

        return category

    @jwt_required(fresh=False)
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        categories = CategoryModel.query.all()
        return categories

@blp.route("/item")
class Item(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, data):
        item = ItemModel.query.filter_by(item_name=data["item_name"]).first()
        if item:
            abort(409, message="Item already exists")

        item = ItemModel(item_name= data["item_name"],price=data["price"], category_id=data["category_id"])

        db.session.add(item)
        db.session.commit()

        return item

    @jwt_required(fresh=False)
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        items = ItemModel.query.all()
        return items