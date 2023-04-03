
from flask.views import MethodView

from ..schemas.invoice_schema import InvoiceSchema
from ..schemas.purchasingschema import PurchasingSchema, PurchaseUpdateSchema,PlainPurchasingSchema
from flask_smorest import Blueprint,abort
from invapp.models.transactions.purchasing_models import PurchaseModel
from invapp.models.transactions.invoice_model import InvoiceModel
from ..signals import increase_stock_addition,expense_addition
from flask_jwt_extended import jwt_required,get_current_user, get_jwt_identity

blp = Blueprint("Purchasing",__name__,description="Purchasing controls")

@blp.route("/purchase")
class PurchasingView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainPurchasingSchema)
    @blp.response(201, InvoiceSchema)
    def post(self, data):
        invoice = InvoiceModel.query.get(data["invoice_id"])
        if not invoice:
            abort(400, message="Invoice does not exists")

        cost = 0
        for item in data["items_list"]:
            existing_inv = PurchaseModel.query.filter_by(invoice_id=data["invoice_id"], item_id=item["item_id"]).first()
            if existing_inv:
                abort(400, message="Item is already in invoice")
            item_cost = item["quantity"] * item["buying_price"]
            cost += item_cost
            line = PurchaseModel(item_id=item["item_id"],description=item["description"],item_cost=item_cost ,item_quantity=item["quantity"], buying_price=item["buying_price"], invoice_id=invoice.id)
            line.save_to_db()
            line.invoice = invoice

            if invoice.destination_type == "stores":
                increase_stock_addition(item_id=item["item_id"], invoice_id=invoice.id,
                                                 date=invoice.date, quantity=item["quantity"], unit_cost=item["buying_price"])

            if invoice.destination_type == "expense":
                expense_addition(item_id=item["item_id"], invoice_id=invoice.id, date=invoice.date, quantity=item["quantity"], unit_cost=item["buying_price"])

        if invoice.amount > cost or invoice.amount < cost:
            invoice.matched_to_lines = "unmatched"
            invoice.update_db()
        else:
            invoice.matched_to_lines = "matched"
            invoice.update_db()

        Invoice_lines = InvoiceModel.query.get(data["invoice_id"])
        return Invoice_lines

    @jwt_required(fresh=True)
    @blp.response(200,PurchasingSchema(many=True))
    def get(self):
        purchases = PurchaseModel.query.all()
        return purchases

@blp.route("/purchase/<int:id>")
class PurchaseManipulateView(MethodView):
    @jwt_required(fresh=True)
    def delete(self, id):
        transaction = PurchaseModel.query.get_or_404(id)
        transaction.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.response(200, PurchasingSchema)
    def get(self, id):
        transaction = PurchaseModel.query.get_or_404(id)
        return transaction

    @jwt_required(fresh=True)
    @blp.arguments(PurchaseUpdateSchema)
    @blp.response(200, PurchasingSchema)
    def patch(self,data, id):
        transaction = PurchaseModel.query.get_or_404(id)

        invoice = InvoiceModel.query.get_or_404(data["invoice_id"])

        transaction.update_from_dict(data)
        transaction.invoice = invoice
        transaction.item_cost += data["item_cost"]
        transaction.update_db()


        if invoice.amount > transaction.item_cost or invoice.amount < transaction.item_cost:
            invoice.matched_to_lines = "unmatched"
            invoice.update_db()
        else:
            invoice.matched_to_lines = "matched"
            invoice.update_db()

        if invoice.destination_type == "stores":
            increase_stock_addition(item_id=transaction.item_id, invoice_id=invoice.id,
                                    date=invoice.date, quantity=transaction.quantity, unit_cost=transaction.buying_price)

        if invoice.destination_type == "expense":
            expense_addition(item_id=transaction.item_id, invoice_id=invoice.id, date=invoice.date,
                             quantity=transaction.quantity, unit_cost=transaction.buying_price)
        return transaction





