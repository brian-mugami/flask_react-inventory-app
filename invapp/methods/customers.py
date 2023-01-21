from ..db import db
from ..models.customermodels import CustomerModel,CustomerAccountModel
from flask.views import MethodView
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_smorest import Blueprint,abort
from ..schemas.customerschema import CustomerAccountSchema,CustomerSchema

blp = Blueprint("Customers", __name__, description="Operations on customers")

@blp.route("/customer/account")
class CustomerAccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(CustomerAccountSchema)
    @blp.response(200, CustomerAccountSchema)
    def post(self, data):
        account = CustomerAccountModel.query.filter_by(account_name=data["account_name"]).first()
        if account:
            abort(409, message="Account already exists")

        account = CustomerAccountModel(account_name= data["account_name"],account_number=data["account_number"],
                                   account_description= data["account_description"])

        db.session.add(account)
        db.session.commit()
        return account
    @jwt_required(fresh=False)
    @blp.response(201, CustomerAccountSchema(many=True))
    def get(self):
        accounts = CustomerAccountModel.query.all()
        return accounts

@blp.route("/customer/account/<int:id>")
class CustomerEditView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, CustomerAccountSchema)
    def delete(self, id):
        account = CustomerAccountModel.query.get_or_404(id)
        db.session.delete(account)
        db.session.delete()

        return account
    @jwt_required(fresh=True)
    @blp.response(202, CustomerAccountSchema)
    def get(self, id):
        account = CustomerAccountModel.query.get_or_404(id)

        return account
@blp.route("/customer")
class Customer(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(CustomerSchema)
    @blp.response(201, CustomerSchema)
    def post(self, data):
        customer = CustomerModel.query.filter_by(customer_name=data["customer_name"]).first()
        if customer:
            abort(409, message="Customer already exists")

        customer = CustomerModel(customer_name= data["customer_name"], account_id=data["account_id"])

        db.session.add(customer)
        db.session.commit()

        return customer

    @jwt_required(fresh=False)
    @blp.response(200, CustomerSchema(many=True))
    def get(self):
        customers = CustomerModel.query.all()

        return customers

@blp.route("/customer/<int:id>")
class ItemView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, CustomerSchema)
    def delete(self, id):
        supplier = CustomerModel.query.get_or_404(id)
        db.session.delete(supplier)
        db.session.commit()
        return supplier
    @jwt_required(fresh=True)
    @blp.response(202, CustomerSchema)
    def get(self, id):
        supplier = CustomerModel.query.get_or_404(id)

        return supplier