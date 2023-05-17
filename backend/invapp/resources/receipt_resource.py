import datetime
import traceback

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from ..models.masters import CustomerModel, AccountModel
from ..models.transactions.customer_balances_model import CustomerBalanceModel
from ..models.transactions.customer_payments_model import CustomerPaymentModel
from ..models.transactions.receipt_model import ReceiptModel
from ..models.transactions.sales_accounting_models import SalesAccountingModel
from ..schemas.receiptschema import ReceiptSchema, ReceiptPaymentSchema, ReceiptVoidSchema
from ..signals import void_receipt, SignalException


blp = Blueprint("receipts", __name__, description="Receipt creation")

@blp.route("/receipt/void/<int:id>")
class ReceiptVoidView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ReceiptVoidSchema)
    def post(self, data, id):
        receipt = ReceiptModel.query.get_or_404(id)
        if receipt.voided == True:
            abort(400, message="Receipt is already voided")
        if receipt.status != "not paid":
            abort(400, message="You cannot void a receipt with payments")
        receipt.reason = data.get("reason")
        receipt.void_receipt()
        receipt.update_db()
        try:
            void_receipt(receipt_id=receipt.id)
        except SignalException as e:
            traceback.print_exc()
            abort(500, message=f'{str(e)}')

@blp.route("/receipt/payment/<int:id>")
class ReceiptPaymentView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ReceiptPaymentSchema)
    @blp.response(201, ReceiptPaymentSchema)
    def post(self, data, id):

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

        data.pop("receipt_account")
        payment = CustomerPaymentModel(
        **data,
        receipt_id=id,
        receive_account_id=account.id,
        approval_status = "pending approval",
        payment_status = "not_paid"
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
        receipts = ReceiptModel.query.order_by(ReceiptModel.date.desc()).all()
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
        if receipt.status != "not paid":
            abort(404, message="This receipt has payment already processed, please void it")
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
        if receipt.status != "not paid":
            abort(400, message="You cannot edit an already paid receipt")
        if receipt.voided == True:
            abort(400, message="This receipt is already voided")
        data.pop("customer_name", None)
        receipt.description = data.get("description")
        receipt.currency = data.get("currency")
        receipt.amount = data.get("amount")
        receipt.customer = customer
        receipt.update_date = datetime.datetime.utcnow()
        receipt.update_db()
        return receipt