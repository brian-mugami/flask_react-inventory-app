from flask import jsonify
from sqlalchemy import func

from ..db import db
from sqlalchemy.exc import IntegrityError
from ..models import AccountModel
from invapp.models.masters.customermodels import CustomerModel
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint,abort
from ..schemas.customerschema import CustomerSchema,CustomerUpdateSchema
from ..schemas.accountsschema import AccountSchema, AccountUpdateSchema

blp = Blueprint("Customers", __name__, description="Operations on customers")

@blp.route("/customer/account")
class CustomerAccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(AccountSchema)
    @blp.response(200, AccountSchema)
    def post(self, data):
        account = AccountModel.query.filter_by(
            account_name=data["account_name"],
            account_category="Customer Account"
        ).first()
        if account:
            abort(409, message="Account already exists")

        account = AccountModel(account_name= data["account_name"],account_number=data["account_number"],
                                   account_type= data["account_type"],account_description= data["account_description"], account_category="Customer Account", )

        db.session.add(account)
        db.session.commit()
        return account
    @jwt_required(fresh=False)
    @blp.response(201, AccountSchema(many=True))
    def get(self):
        accounts = AccountModel.query.filter_by(account_category="Customer Account").all()

        return accounts

@blp.route("/customer/account/<int:id>")
class CustomerEditView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(204, AccountSchema)
    def delete(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Customer Account":
            abort(400, message="This is not a customer account")
        db.session.delete(account)
        db.session.commit()
        return jsonify({"msg": "deleted successfully"})

    @jwt_required(fresh=True)
    @blp.response(202, AccountSchema)
    def get(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Customer Account":
            abort(400, message="This is not a customer account")
        return account

    @jwt_required(fresh=True)
    @blp.arguments(AccountUpdateSchema)
    def patch(self, data, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Customer Account":
            abort(400, message="This is not a customer account")
        account.account_name = data["account_name"]
        account.account_description = data["account_description"]
        account.account_number = data["account_number"]
        account.account_type = data["account_type"]
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
        customer_account = AccountModel.query.filter_by(account_name=data["account_name"], account_category="Customer Account").first()
        if customer_account is None:
            abort(404, message="Account does not exist")

        account_id = customer_account.id

        customer = CustomerModel(customer_name=data["customer_name"], account_id=account_id, customer_phone_no=data["customer_phone_no"],customer_email=data["customer_email"], is_active=data["is_active"])
        try:
            db.session.add(customer)
            db.session.commit()
            return customer
        except IntegrityError as e:
            abort(500, message="Please provide unique email and phone number for this customer")

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
    @blp.arguments(CustomerUpdateSchema)
    @blp.response(201, CustomerSchema)
    def patch(self, data, id):
        customer = CustomerModel.query.get_or_404(id)
        customer_account = AccountModel.query.filter_by(account_name=data["account_name"],
                                                        account_category="Customer Account").first()
        if customer_account is None:
            abort(404, message="Account does not exist")
        if customer:
            customer.customer_name = data["customer_name"]
            customer.customer_phone_no = data["customer_phone_no"]
            customer.customer_email = data["customer_email"]
            customer.is_active = data["is_active"]

            customer.account_id = customer_account.id

            db.session.commit()

@blp.route("/customer/count")
class CustomerCount(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        customers = db.session.execute(CustomerModel.query.filter_by(is_active=True).statement.with_only_columns([func.count()]).order_by(None)).scalar()
        #customers = db.session.execute('select count(id) as c from customers where is_active= true').scalar()
        return jsonify({"customers": customers}), 202
