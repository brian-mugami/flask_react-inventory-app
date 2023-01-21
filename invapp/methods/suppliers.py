from ..db import db
from ..models.suppliermodels import SupplierModel,SupplierAccountModel
from flask.views import MethodView
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_smorest import Blueprint,abort
from ..schemas.supplierschema import SupplierAccountSchema, SupplierSchema

blp = Blueprint("Suppliers", __name__, description="Operations on suppliers")

@blp.route("/supplier/account")
class SupplierAccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(SupplierAccountSchema)
    @blp.response(200, SupplierAccountSchema)
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
class SupplierEditView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, SupplierAccountSchema)
    def delete(self, id):
        account = SupplierAccountModel.query.get_or_404(id)
        db.session.delete(account)
        db.session.delete()

        return account
    @jwt_required(fresh=True)
    @blp.response(202, SupplierAccountSchema)
    def get(self, id):
        account = SupplierAccountModel.query.get_or_404(id)

        return account
@blp.route("/supplier")
class Supplier(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(SupplierSchema)
    @blp.response(201, SupplierSchema)
    def post(self, data):
        supplier = SupplierModel.query.filter_by(supplier_name=data["supplier_name"]).first()
        if supplier:
            abort(409, message="Supplier already exists")

        supplier = SupplierModel(supplier_name= data["supplier_name"], account_id=data["account_id"])

        db.session.add(supplier)
        db.session.commit()

        return supplier

    @jwt_required(fresh=False)
    @blp.response(200, SupplierSchema(many=True))
    def get(self):
        suppliers = SupplierModel.query.all()

        return suppliers

@blp.route("/supplier/<int:id>")
class ItemView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, SupplierSchema)
    def delete(self, id):
        supplier = SupplierModel.query.get_or_404(id)
        db.session.delete(supplier)
        db.session.commit()
        return supplier
    @jwt_required(fresh=True)
    @blp.response(202, SupplierSchema)
    def get(self, id):
        supplier = SupplierModel.query.get_or_404(id)

        return supplier