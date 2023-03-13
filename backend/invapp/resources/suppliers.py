from flask import jsonify
from sqlalchemy import func

from ..db import db
from ..models.suppliermodels import SupplierModel,SupplierAccountModel
from flask.views import MethodView
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_smorest import Blueprint,abort
from ..schemas.supplierschema import SupplierAccountSchema, SupplierSchema, SupplierAccountUpdateSchema, SupplierCountSchema

blp = Blueprint("Suppliers", __name__, description="Operations on suppliers")

@blp.route("/supplier/account")
class SupplierAccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(SupplierAccountSchema)
    @blp.response(201, SupplierAccountSchema)
    def post(self, data):
        account = SupplierAccountModel.query.filter_by(account_name=data["account_name"]).first()
        if account:
            abort(409, message="Account already exists")

        account = SupplierAccountModel(account_name= data["account_name"],account_number=data["account_number"],
                                   account_description= data["account_description"])

        db.session.add(account)
        db.session.commit()
        return account
    @jwt_required(fresh=False)
    @blp.response(201, SupplierAccountSchema(many=True))
    def get(self):
        accounts = SupplierAccountModel.query.all()
        return accounts

@blp.route("/supplier/account/<int:id>")
class SupplierAccountView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(204, SupplierAccountSchema)
    def delete(self, id):
        account = SupplierAccountModel.query.get_or_404(id)
        db.session.delete(account)
        db.session.commit()

        return account

    @jwt_required(fresh=True)
    @blp.response(202, SupplierAccountSchema)
    def get(self, id):
        account = SupplierAccountModel.query.get_or_404(id)
        return account

    @jwt_required(fresh=True)
    @blp.arguments(SupplierAccountUpdateSchema)

    def patch(self, data, id):
        account = SupplierAccountModel.query.get_or_404(id)
        account.account_name = data["account_name"]
        account.account_description = data["account_description"]
        account.account_number = data["account_number"]
        db.session.commit()
        return jsonify({"message": "account updated"}), 202

@blp.route("/supplier")
class Supplier(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(SupplierSchema)
    @blp.response(201, SupplierSchema)
    def post(self, data):
        supplier = SupplierModel.query.filter_by(supplier_name=data["supplier_name"]).first()
        if supplier:
            abort(409, message="Supplier already exists")
        account = SupplierAccountModel.query.filter_by(account_name=data["account_name"]).first()
        if account is None:
            abort(404, message="Account does not exist")

        account_id = account.id

        supplier = SupplierModel(supplier_name=data["supplier_name"], account_id=account_id,
                                 supplier_contact=data["supplier_contact"],supplier_site=data["supplier_site"], is_active=data["is_active"])

        db.session.add(supplier)
        db.session.commit()

        return supplier

    @jwt_required(fresh=False)
    @blp.response(200, SupplierSchema(many=True))
    def get(self):
        suppliers = SupplierModel.query.all()

        return suppliers

@blp.route("/supplier/<int:id>")
class SupplierView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, SupplierSchema)
    def delete(self, id):
        supplier = SupplierModel.query.get_or_404(id)
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({"message": "supplier deleted"}), 204

    @jwt_required(fresh=True)
    @blp.response(202, SupplierSchema)
    def get(self, id):
        supplier = SupplierModel.query.get_or_404(id)

        return supplier

    @jwt_required(fresh=True)
    @blp.arguments(SupplierSchema)
    @blp.response(201, SupplierSchema)
    def patch(self, data, id):
        supplier = SupplierModel.query.get_or_404(id)
        if supplier:
            supplier.supplier_name = data["supplier_name"]
            supplier.supplier_contact = data["supplier_contact"]
            supplier.supplier_site = data["supplier_site"]
            supplier.is_active = data["is_active"]

            supplier_account = SupplierAccountModel.query.filter_by(account_name=data["account_name"]).first()
            if supplier_account is None:
                abort(404, message="Account does not exist")

            supplier.account_id = supplier_account.id

            db.session.commit()

@blp.route("/supplier/count")
class SupplierCount(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        suppliers = db.session.execute(SupplierModel.query.filter_by(is_active=True).statement.with_only_columns([func.count()]).order_by(None)).scalar()
        #suppliers = db.session.execute('select count(id) as c from suppliers where is_active= true').scalar()
        return jsonify({"suppliers": suppliers}), 202
