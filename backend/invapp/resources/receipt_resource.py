import datetime

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from invapp.models import CustomerModel
from invapp.models.transactions.receipt_model import ReceiptModel
from invapp.schemas.receiptschema import ReceiptSchema
from invapp.signals import add_customer_balance, SignalException

receipt_bp = Blueprint("recipts", __name__, url_prefix="/receipts", description="Receipt creation")

@receipt_bp.route("/")
class ReceiptView(MethodView):
    @jwt_required(fresh=True)
    @receipt_bp.response(200, ReceiptSchema(many=True))
    def get(self):
        receipts = ReceiptModel.query.all()
        return receipts

    @jwt_required(fresh=True)
    @receipt_bp.arguments(ReceiptSchema)
    @receipt_bp.response(201, ReceiptSchema)
    def post(self, data):
        customer = CustomerModel.query.get(data["customer_id"])
        if customer is None:
            abort(404, message="Customer not found")
        receipt = ReceiptModel(**data)
        receipt.customer = customer
        receipt.save_to_db()
        if receipt.amount > 0.00:
            try:
                add_customer_balance(customer_id=receipt.customer_id,sale_id=receipt.id,receipt_amount=receipt.amount,currency=receipt.currency)
                return receipt
            except SignalException as e:
                receipt.delete_from_db()
                abort(500, message="Did not add customer balance")

@receipt_bp.route("/<int:id>")
class ReceiptMethodView(MethodView):
    @jwt_required(fresh=True)
    def delete(self, id):
        receipt = ReceiptModel.query.get_or_404(id)
        receipt.delete_from_db()
        return {"message":"deleted"}, 204

    @jwt_required(fresh=True)
    @receipt_bp.response(200, ReceiptSchema)
    def get(self,id):
        receipt = ReceiptModel.query.get_or_404(id)
        return receipt

    @jwt_required(fresh=True)
    @receipt_bp.arguments(ReceiptSchema)
    @receipt_bp.response(200, ReceiptSchema)
    def patch(self, data, id):
        receipt = ReceiptModel.query.get_or_404(id)
        customer = CustomerModel.query.get(data["customer_id"])
        if not customer:
            abort(404, message="Customer not found")
        receipt.update_from_dict(data)
        receipt.customer = customer
        receipt.update_date = datetime.datetime.utcnow()
        receipt.update_db()
        return receipt