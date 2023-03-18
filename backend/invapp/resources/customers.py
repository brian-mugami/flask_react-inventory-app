from flask import jsonify
from sqlalchemy import func

from ..db import db
from ..models.customermodels import CustomerModel,CustomerAccountModel
from flask.views import MethodView
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_smorest import Blueprint,abort
from ..schemas.customerschema import CustomerAccountSchema,CustomerSchema,CustomerAccountUpdateSchema

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
    @blp.response(204, CustomerAccountSchema)
    def delete(self, id):
        account = CustomerAccountModel.query.get_or_404(id)
        db.session.delete(account)
        db.session.commit()
        return jsonify({"msg": "deleted successfully"})

    @jwt_required(fresh=True)
    @blp.response(202, CustomerAccountSchema)
    def get(self, id):
        account = CustomerAccountModel.query.get_or_404(id)
        return account

    @jwt_required(fresh=True)
    @blp.arguments(CustomerAccountUpdateSchema)
    def patch(self, data, id):
        account = CustomerAccountModel.query.get_or_404(id)
        account.account_name = data["account_name"]
        account.account_description = data["account_description"]
        account.account_number = data["account_number"]
        db.session.commit()
        return jsonify({"message": "account updated"}), 202

@blp.route("/customer")
class Customer(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(CustomerSchema)
    @blp.response(201, CustomerSchema)
    def post(self, data):
        customer = CustomerModel.query.filter_by(customer_name=data["customer_name"]).first()
        if customer:
            abort(409, message="Customer already exists")
        customer_account = CustomerAccountModel.query.filter_by(account_name=data["account_name"]).first()
        if customer_account is None:
            abort(404, message="Category does not exist")

        account_id = customer_account.id

        customer = CustomerModel(customer_name=data["customer_name"], account_id=account_id, customer_contact=data["customer_contact"], is_active=data["is_active"])

        db.session.add(customer)
        db.session.commit()

        return customer

    @jwt_required(fresh=False)
    @blp.response(200, CustomerSchema(many=True))
    def get(self):
        customers = CustomerModel.query.all()

        return customers

@blp.route("/customer/<int:id>")
class CustomerView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, CustomerSchema)
    def delete(self, id):
        customer = CustomerModel.query.get_or_404(id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"msg": "deleted successfully"})

    @jwt_required(fresh=True)
    @blp.response(202, CustomerSchema)
    def get(self, id):
        customer = CustomerModel.query.get_or_404(id)

        return customer

    @jwt_required(fresh=True)
    @blp.arguments(CustomerSchema)
    @blp.response(201, CustomerSchema)
    def patch(self, data, id):
        customer = CustomerModel.query.get_or_404(id)
        if customer:
            customer.customer_name = data["customer_name"]
            customer.customer_contact = data["customer_contact"]
            customer.is_active = data["is_active"]

            customer_account = CustomerAccountModel.query.filter_by(account_name=data["account_name"]).first()
            if customer_account is None:
                abort(404, message="Category does not exist")

            customer.account_id = customer_account.id

            db.session.commit()

@blp.route("/customer/count")
class CustomerCount(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        customers = db.session.execute(CustomerModel.query.filter_by(is_active=True).statement.with_only_columns([func.count()]).order_by(None)).scalar()
        #customers = db.session.execute('select count(id) as c from customers where is_active= true').scalar()
        return jsonify({"customers": customers}), 202
