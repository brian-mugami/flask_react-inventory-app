import datetime
import traceback

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint,abort

from ..models import AccountModel, CustomerModel
from ..models.transactions.receipt_model import ReceiptModel
from ..models.transactions.sales_accounting_models import CustomerPayAccountingModel
from ..schemas.customerpaymentschema import PlainCustomerPaymentSchema,PaymentUpdateSchema, SearchReceiptToPaySchema
from ..models.transactions.customer_payments_model import CustomerPaymentModel
from ..models.transactions.customer_balances_model import CustomerBalanceModel
from flask_jwt_extended import jwt_required

from ..schemas.receiptschema import ReceiptSchema
from ..signals import add_customer_balance, receive_payment, manipulate_bank_balance, SignalException

blp = Blueprint("Customer payments", __name__, description="Customer payments")

@blp.route("/customer/payment/<int:id>/account")
class PaymentAccountingView(MethodView):
    @jwt_required(fresh=True)
    def get(self, id):
        accounts = []
        payment = CustomerPaymentModel.query.get(id)
        if not payment:
            abort(404, message="Payment does not exist")
        payment_accounting = CustomerPayAccountingModel.query.filter_by(payment_id=payment.id).all()
        if not payment_accounting:
            abort(404, message="Accounting has not been done")
        for accounting in payment_accounting:
            debit_account= AccountModel.query.get(accounting.debit_account_id)
            credit_account = AccountModel.query.get(accounting.credit_account_id)
            account = {"debit_account": debit_account.account_name,
                       "credit_account": credit_account.account_name,
                       "credit_amount": accounting.credit_amount,
                       "debit_amount":accounting.debit_amount}
            accounts.append(account)

        return jsonify({"accounting": accounts})

@blp.route("/customer/payment/search/")
class Invoices(MethodView):

    @jwt_required(fresh=True)
    @blp.arguments(SearchReceiptToPaySchema, location="query")
    @blp.response(202,ReceiptSchema(many=True))
    def get(self, data):
        name = data.get("customer_name", "")
        ids = []
        customers = CustomerModel.query.filter(CustomerModel.customer_name.contains(name)).all()
        if len(customers) < 1:
            abort(404, message="No such customer has an unpaid receipt")
        for customer in customers:
            ids.append(customer.id)
        #invoices = InvoiceModel.query.filter(InvoiceModel.status.in_(["partially paid", "not paid"]))
        customer_receipts = ReceiptModel.query.filter(ReceiptModel.customer_id.in_(ids),ReceiptModel.status.in_(["partially paid", "not paid"])).order_by(ReceiptModel.date.desc()).all()
        print(customer_receipts)

        return customer_receipts

@blp.route("/customer/payment")
class PaymentView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainCustomerPaymentSchema)
    @blp.response(201, PlainCustomerPaymentSchema)
    def post(self, data):
        receipt = ReceiptModel.query.get(data["receipt_id"])
        if not receipt:
            abort(404, message="Receipt does not exist")
        customer_payment = CustomerPaymentModel.query.filter_by(receipt_id=data["receipt_id"]).order_by(CustomerPaymentModel.date.desc()).first()
        if customer_payment.payment_status == "fully_paid":
            abort(400, message="This payment is already created and fully paid")
        account = AccountModel.query.filter_by(account_name=data["receipt_account"]).first()
        if not account:
            abort(404, message="Account not found")
        customer_amount = CustomerBalanceModel.query.filter_by(receipt_id=data["receipt_id"], currency=data["currency"]).first()
        if not customer_amount:
            abort(404, message="This customer has no balance")

        status = ""
        if customer_amount.balance < data["amount"]:
            status = "over_paid"
        if customer_amount.balance > data["amount"]:
            status = "partially_paid"
        elif customer_amount.balance == data["amount"]:
            status = "fully_paid"
        elif data["amount"] == 0:
            status = "not_paid"

        data.pop("receipt_account")
        payment = CustomerPaymentModel(
        **data,
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

    @jwt_required(fresh=True)
    @blp.response(200, PlainCustomerPaymentSchema(many=True))
    def get(self):
        payments = CustomerPaymentModel.query.order_by(CustomerPaymentModel.date.desc()).all()
        return payments

@blp.route("/customer/payment/<int:id>")
class PaymentMainView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(201, PlainCustomerPaymentSchema)
    def get(self, id):
        payment = CustomerPaymentModel.query.get_or_404(id)
        return payment

    @jwt_required(fresh=True)
    def delete(self, id):
        transaction = CustomerPaymentModel.query.get_or_404(id)
        transaction.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.arguments(PaymentUpdateSchema)
    @blp.response(202, PlainCustomerPaymentSchema)
    def patch(self, data, id):
        sale_amount = CustomerBalanceModel.query.filter_by(sale_id=data["sale_id"], currency=data["currency"]).first()
        payment = CustomerPaymentModel.query.get_or_404(id)
        status = ""
        if payment and sale_amount:
            payment.amount = data["amount"]
            payment.approved = False
            payment.receive_account_id = data["receive_account_id"]
            payment.sale_id = data["sale_id"]
            payment.update_date = datetime.datetime.utcnow()

            if sale_amount.balance < payment.amount:
                status= "over_paid"
            elif sale_amount.balance > payment.amount:
                status = "partially_paid"
            elif sale_amount.balance == payment.amount:
                status = "fully_paid"
            elif payment.balance <= 0:
                status = "not_paid"

            payment.payment_status = status
        payment.update_db()

        return payment

@blp.route("/customer/payment/approve/<int:id>")
class PaymentApproveView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202,PlainCustomerPaymentSchema)
    def post(self, id):
        payment = CustomerPaymentModel.query.get_or_404(id)
        customer_account_id = payment.receipt.customer.account_id
        customer_id = payment.receipt.customer_id
        receipt_amount = payment.receipt.amount
        receipt_id = payment.receipt_id
        currency = payment.receipt.currency
        if payment.approved:
            abort(400, message="This payment is already approved!!")
        payment.approve_payment()
        try:
            balance=add_customer_balance(customer_id=customer_id, receipt_amount=receipt_amount, paid=payment.amount, receipt_id=receipt_id, currency=currency)
            receive_payment(customer_account_id=customer_account_id,bank_account=payment.receive_account_id,amount=payment.amount,payment_id=payment.id, balance_id=balance)
            manipulate_bank_balance(bank_account_id=payment.receive_account_id,receipt_id=receipt_id, amount=receipt_amount, currency=currency)
            return payment
        except SignalException as e:
            abort(500, message=f"{str(e)}")
