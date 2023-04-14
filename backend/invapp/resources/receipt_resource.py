import datetime

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from invapp.models import CustomerModel
from invapp.models.transactions.receipt_model import ReceiptModel
from invapp.schemas.receiptschema import ReceiptSchema

blp = Blueprint("receipts", __name__, description="Receipt creation")

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
        #customer = CustomerModel.query.filter_by(customer_name=data["customer_name"]).first()
        customer = CustomerModel.query.get(data["customer_id"])
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