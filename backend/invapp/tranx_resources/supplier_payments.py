import datetime

from flask.views import MethodView
from flask_smorest import Blueprint,abort

from ..models import AccountModel, SupplierModel
from ..models.transactions.invoice_model import InvoiceModel
from ..schemas.invoice_schema import SearchInvoiceToPaySchema, InvoiceSchema, InvoicePaymentSchema
from ..schemas.paymentsschema import PlainPaymentSchema, PaymentUpdateSchema
from ..models.transactions.supplier_payment_models import SupplierPaymentModel
from ..models.transactions.supplier_balances_model import SupplierBalanceModel
from flask_jwt_extended import jwt_required
from ..signals import add_supplier_balance, make_payement, manipulate_bank_balance, SignalException

blp = Blueprint("payments", __name__, description="Supplier payments")



@blp.route("/payment/search/")
class Invoices(MethodView):

    @jwt_required(fresh=True)
    @blp.arguments(SearchInvoiceToPaySchema, location="query")
    @blp.response(202,InvoiceSchema(many=True))
    def get(self, data):
        name = data.get("supplier_name", "")
        ids = []
        suppliers = SupplierModel.query.filter(SupplierModel.supplier_name.ilike(name)).all()
        for supplier in suppliers:
            ids.append(supplier.id)
        #invoices = InvoiceModel.query.filter(InvoiceModel.status.in_(["partially paid", "not paid"]))
        supplier_invoices = InvoiceModel.query.filter(InvoiceModel.supplier_id.in_(ids),InvoiceModel.status.in_(["partially paid", "not paid"])).order_by(InvoiceModel.date.desc()).all()

        return supplier_invoices

@blp.route("/payment")
class PaymentView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainPaymentSchema)
    @blp.response(201, PlainPaymentSchema)
    def post(self, data):
        invoice = InvoiceModel.query.get(data["invoice_id"])
        if not invoice:
            abort(404, message="Could not find invoice")
        account = AccountModel.query.get(data["bank_account_id"])
        if not account:
            abort(404, message="Account can not be found")
        if account.account_category != "Bank Account":
            abort(400, message="This is not a bank account")
        purchase_amount = SupplierBalanceModel.query.filter_by(invoice_id=data["invoice_id"], currency=data["currency"]).first()
        status = ""
        if purchase_amount.balance < data["amount"]:
            abort(400, message="Amount is higher than the balance")
        elif purchase_amount.balance > data["amount"]:
            status = "partially paid"
        elif purchase_amount.balance == data["amount"]:
            status = "fully paid"
        elif data["amount"] <= 0:
            status = "not paid"

        payment = SupplierPaymentModel(
        amount = data["amount"],
        bank_account_id = data["bank_account_id"],
        invoice_id = data["invoice_id"],
        currency = data["currency"],
        approved = False,
        payment_status = status
        )
        payment.invoice = invoice
        payment.account = account
        payment.save_to_db()
        invoice.status = payment.payment_status
        invoice.update_db()
        return payment

    @jwt_required(fresh=True)
    @blp.response(200, PlainPaymentSchema(many=True))
    def get(self):
        payments = SupplierPaymentModel.query.order_by(SupplierPaymentModel.date.desc()).all()
        return payments

@blp.route("/payment/<int:id>")
class PaymentMainView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(201, PlainPaymentSchema)
    def get(self, id):
        payment = SupplierPaymentModel.query.get_or_404(id)
        return payment

    @jwt_required(fresh=True)
    def delete(self, id):
        transaction = SupplierPaymentModel.query.get_or_404(id)
        transaction.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.arguments(PaymentUpdateSchema)
    @blp.response(202, PlainPaymentSchema)
    def patch(self, data, id):
        payment = SupplierPaymentModel.query.get_or_404(id)
        purchase_amount = SupplierBalanceModel.query.filter_by(invoice_id=data["invoice_id"], currency=data["currency"]).first()
        invoice = InvoiceModel.query.get(data["invoice_id"])
        if not invoice:
            abort(404, message="Could not find invoice")
        account = AccountModel.query.get(data["bank_account_id"])
        if not account:
            abort(404, message="Account can not be found")
        status = ""
        if payment and purchase_amount:
            payment.amount = data["amount"]
            payment.approved = False
            payment.pay_account_id = data["bank_account_id"]
            payment.invoice_id = data["invoice_id"]
            payment.update_date = datetime.datetime.utcnow()
            payment.invoice = invoice
            payment.account = account

            if purchase_amount.balance < payment.amount:
                abort(400, message="Amount higher than the balance")
            elif purchase_amount.balance > payment.amount:
                status = "partially paid"
            elif purchase_amount.balance == payment.amount:
                status = "fully paid"
            elif payment.balance <= 0:
                status = "not paid"

            payment.payment_status = status
            payment.invoice.status = status
            payment.invoice = invoice
        payment.update_db()

        return payment

@blp.route("/payment/approve/<int:id>")
class PaymentApproveView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, PlainPaymentSchema)
    def post(self, id):
        payment = SupplierPaymentModel.query.get_or_404(id)
        supplier_account_id = payment.invoice.supplier.account_id
        supplier_id = payment.invoice.supplier_id
        invoice_amount = payment.invoice.amount
        invoice_id = payment.invoice_id
        currency = payment.invoice.currency
        if payment.approved:
            abort(400, message="This payment is already approved!!")
        payment.approve_payment()
        try:
            balance = add_supplier_balance(supplier_id=supplier_id, invoice_amount=invoice_amount, paid=payment.amount, invoice_id=invoice_id, currency=currency)
            make_payement(supplier_account_id=supplier_account_id,credit_account=payment.bank_account_id,amount=payment.amount,payment_id=payment.id,balance_id=balance)
            manipulate_bank_balance(bank_account_id=payment.bank_account_id,invoice_id=invoice_id,amount=-payment.amount, currency=currency)
            return payment
        except SignalException as e:
            abort(400, message=f"{str(e)}")


