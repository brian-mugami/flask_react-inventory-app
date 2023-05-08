from flask import jsonify
from ..db import db
from ..models.masters import AccountModel
from ..models.masters.itemmodels import CategoryModel, ItemModel, LotModel
from flask_jwt_extended import jwt_required
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from ..schemas.itemschema import LotSchema, CategorySchema, ItemSchema,  PlainCategorySchema
from ..schemas.accountsschema import AccountSchema,AccountUpdateSchema

blp = Blueprint("Items", __name__, description="Actions on items")

@blp.route("/category/account")
class Categoryaccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(AccountSchema)
    @blp.response(201, AccountSchema)
    def post(self, data):
        account = AccountModel.query.filter_by(
            account_name=data["account_name"],
            account_category="Item Account"
        ).first()
        if account:
            abort(409, message="Account already exists")

        account = AccountModel(account_name= data["account_name"],account_number=data["account_number"],
                                   account_description= data["account_description"], account_category="Item Account", account_type= data["account_type"])

        db.session.add(account)
        db.session.commit()
        return account
    @jwt_required(fresh=False)
    @blp.response(200, AccountSchema(many=True))
    def get(self):
        accounts = AccountModel.query.filter_by(account_category="Item Account").all()
        return accounts

@blp.route("/category/account/<int:id>")
class CategoryaccountView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, AccountSchema)
    def delete(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Item Account":
            abort(400, message="This is not an item account")
        db.session.delete(account)
        db.session.commit()

        return account

    @jwt_required(fresh=True)
    @blp.arguments(AccountUpdateSchema)
    def patch(self, data, id):

        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Item Account":
            abort(400, message="This is not an item account")
        account.account_name = data["account_name"]
        account.account_description = data["account_description"]
        account.account_number = data["account_number"]
        account.account_type = data["account_type"]
        db.session.commit()
        return jsonify({"message": "account updated"}), 202

    @jwt_required(fresh=True)
    @blp.response(202, AccountSchema)
    def get(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Item Account":
            abort(400, message="This is not an item account")

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
        account = AccountModel.query.filter_by(
            account_name=data["account_name"],
            account_category="Item Account"
        ).first()
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
        account = AccountModel.query.filter_by(
            account_name=data["account_name"],
            account_category="Item Account"
        ).first()

        if account is None:
            abort(404, message="Account does not exist")
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
        item = ItemModel(item_name= data["item_name"],price=data["price"], category_id=category_id, unit_type=data["unit_type"], item_unit=data["item_unit"], is_active=data["is_active"])
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
            item.unit_type = data["unit_type"]
            item.item_unit = data["item_unit"]
            item.item_name = data["item_name"]
            item.is_active = data["is_active"]
            category = CategoryModel.query.filter_by(name=data["category_name"]).first()
            if category is None:
                abort(404, message="Category does not exist")

            category_id = category.id
            item.category_id = category_id

            db.session.commit()