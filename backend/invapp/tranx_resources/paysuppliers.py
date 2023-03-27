import datetime
import traceback

from flask.views import MethodView
from flask_smorest import Blueprint,abort
from ..schemas.paymentsschema import PlainPaymentSchema, PaymentUpdateSchema
from ..models.transactions.payment_models import PaymentModel
from ..models.transactions.supplier_balances_model import SupplierBalanceModel
from flask_jwt_extended import jwt_required
from ..signals import add_supplier_balance

blp = Blueprint("payments", __name__, description="Supplier payments")

@blp.route("/payment")
class PaymentView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainPaymentSchema)
    @blp.response(201, PlainPaymentSchema)
    def post(self, data):
        purchase_amount = SupplierBalanceModel.query.filter_by(purchase_id=data["purchase_id"], currency=data["currency"]).first()
        status = ""
        if purchase_amount.balance < data["amount"]:
            abort(400, message="Amount is higher than the balance")
        elif purchase_amount.balance > data["amount"]:
            status = "partially_paid"
        elif purchase_amount.balance == data["amount"]:
            status = "fully_paid"
        elif data["amount"] <= 0:
            status = "not_paid"

        payment = PaymentModel(
        amount = data["amount"],
        pay_account_id = data["pay_account_id"],
        purchase_id = data["purchase_id"],
        currency = data["currency"],
        approved = False,
        payment_status = status
        )
        payment.save_to_db()
        return payment

    @jwt_required(fresh=True)
    @blp.response(200, PlainPaymentSchema(many=True))
    def get(self):
        payments = PaymentModel.query.all()
        return payments

@blp.route("/payment/<int:id>")
class PaymentMainView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(201, PlainPaymentSchema)
    def get(self, id):
        payment = PaymentModel.query.get_or_404(id)
        return payment

    @jwt_required(fresh=True)
    def delete(self, id):
        transaction = PaymentModel.query.get_or_404(id)
        transaction.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.arguments(PaymentUpdateSchema)
    @blp.response(202, PlainPaymentSchema)
    def patch(self, data, id):
        purchase_amount = SupplierBalanceModel.query.filter_by(purchase_id=data["purchase_id"], currency=data["currency"]).first()
        payment = PaymentModel.query.get_or_404(id)
        status = ""
        if payment and purchase_amount:
            payment.amount = data["amount"]
            payment.approved = False
            payment.pay_account_id = data["pay_account_id"]
            payment.purchase_id = data["purchase_id"]
            payment.update_date = datetime.datetime.utcnow()

            if purchase_amount.balance < payment.amount:
                abort(400, message="Amount higher than the balance")
            elif purchase_amount.balance > payment.amount:
                status = "partially_paid"
            elif purchase_amount.balance == payment.amount:
                status = "fully_paid"
            elif payment.balance <= 0:
                status = "not_paid"

            payment.payment_status = status
        payment.save_to_db()

        return payment

@blp.route("/payment/approve/<int:id>")
class PaymentApproveView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(202, PlainPaymentSchema)
    def post(self, id):
        payment = PaymentModel.query.get_or_404(id)
        if payment.approved:
            abort(400, message="This payment is already approved!!")
        payment.approve_payment()
        add_supplier_balance(supplier_id=payment.purchase.supplier_id, amount=payment.purchase.amount, paid=payment.amount, purchase_id=payment.purchase_id)
        return payment
