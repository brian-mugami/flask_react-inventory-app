import datetime
import traceback

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from invapp.models import CustomerModel, AccountModel
from invapp.models.transactions.customer_balances_model import CustomerBalanceModel
from invapp.models.transactions.customer_payments_model import CustomerPaymentModel
from invapp.models.transactions.receipt_model import ReceiptModel
<<<<<<< HEAD
from invapp.schemas.receiptschema import ReceiptSchema
=======
from invapp.models.transactions.sales_accounting_models import SalesAccountingModel
from invapp.schemas.receiptschema import ReceiptSchema, ReceiptPaymentSchema
>>>>>>> main

blp = Blueprint("receipts", __name__, description="Receipt creation")

@blp.route("/receipt/payment/<int:id>")
class ReceiptPaymentView(MethodView):
    @blp.arguments(ReceiptPaymentSchema)
    @blp.response(201, ReceiptPaymentSchema)
    @jwt_required(fresh=True)
    def post(self, data, id):
        status = ""
        account = AccountModel.query.filter_by(account_name=data.get("receipt_account")).first()
        if not account:
            abort(404, message="Account not found")
        receipt = ReceiptModel.query.get(id)
        if not receipt:
            abort(404, message="Receipt does not exist")
        if receipt.status == "fully paid" or receipt.status == "over paid":
            abort(400, message="This receipt is already paid.")
        if receipt.accounted_status == "not_accounted":
            abort(400, "This receipt is not accounted.")

        customer_amount = CustomerBalanceModel.query.filter_by(receipt_id=id, currency=data.get("currency")).first()
        if not customer_amount:
            abort(404, message="This customer has no balance.")

        if customer_amount.balance == 0:
            abort(400, message="This customer has paid his balance.")

        if customer_amount.balance < data["amount"]:
            abort(400, message="This is an amount higher than the balance")
        elif customer_amount.balance > data["amount"]:
            status = "partially_paid"
        elif customer_amount.balance == data["amount"]:
            status = "fully_paid"
        elif data["amount"] <= 0:
            status = "not_paid"
        else:
            status = "over_paid"
        data.pop("receipt_account")
        payment = CustomerPaymentModel(
        **data,
        receipt_id=id,
        receive_account_id=account.id,
        approved = False,
        payment_status = status
        )
        try:
            payment.save_to_db()
            if payment.payment_status == "fully_paid":
                pay_status = "fully paid"
            elif payment.payment_status == "partially_paid":
                pay_status = "partially paid"
            elif payment.payment_status == "not_paid":
                pay_status = "not paid"
            else:
                pay_status = "over paid"
            receipt.status = pay_status
            receipt.update_db()
            return payment
        except:
            traceback.print_exc()
            abort(500, message="Server error, Please create and review the payment again")

@blp.route("/receipt/<int:id>/account")
class ReceiptAccountingView(MethodView):
    @jwt_required(fresh=True)
    def get(self, id):
        accounting = SalesAccountingModel.query.filter_by(receipt_id=id).first()
        if not accounting:
            abort(404, message="Accounting not created for this receipt")
        debit_account = AccountModel.query.get(accounting.debit_account_id)
        credit_account = AccountModel.query.get(accounting.credit_account_id)
        credit_amount = accounting.credit_amount
        debit_amount = accounting.debit_amount

        return jsonify({"debit_account": debit_account.account_name,
                        "credit_account": credit_account.account_name,
                        "credit_amount": credit_amount,
                        "debit_amount": debit_amount})

@blp.route("/receipt")
class ReceiptView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, ReceiptSchema(many=True))
    def get(self):
        receipts = ReceiptModel.query.all()
        return receipts

    @jwt_required(fresh=True)
    @blp.arguments(ReceiptSchema)
    @blp.response(201, ReceiptSchema)
    def post(self, data):
        customer = CustomerModel.query.filter_by(customer_name=data["customer_name"]).first()
        if customer is None:
            abort(404, message="Customer not found")
        data.pop("customer_name", None)
        receipt = ReceiptModel(**data)
        receipt.customer = customer
        try:
            receipt.save_to_db()
            return receipt
        except IntegrityError as e:
            abort(500, message="Ensure details are unique")

@blp.route("/receipt/<int:id>")
class ReceiptMethodView(MethodView):
    @jwt_required(fresh=True)
    def delete(self, id):
        receipt = ReceiptModel.query.get_or_404(id)
        receipt.delete_from_db()
        return {"message":"deleted"}, 204

    @jwt_required(fresh=True)
    @blp.response(200, ReceiptSchema)
    def get(self,id):
        receipt = ReceiptModel.query.get_or_404(id)
        return receipt

    @jwt_required(fresh=True)
    @blp.arguments(ReceiptSchema)
    @blp.response(200, ReceiptSchema)
    def patch(self, data, id):
        receipt = ReceiptModel.query.get_or_404(id)
        customer = CustomerModel.query.filter_by(customer_name=data["customer_name"]).first()
        if not customer:
            abort(404, message="Customer not found")
        data.pop("customer_name", None)
        receipt.update_from_dict(data)
        receipt.customer = customer
        receipt.update_date = datetime.datetime.utcnow()
        receipt.update_db()
        return receipt