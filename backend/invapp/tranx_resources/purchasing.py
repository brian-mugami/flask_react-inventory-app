from flask.views import MethodView

from ..models import ItemModel
from ..schemas.invoice_schema import InvoiceSchema
from ..schemas.purchasingschema import PurchasingSchema,PurchaseUpdateSchema
from flask_smorest import Blueprint,abort
from invapp.models.transactions.purchasing_models import PurchaseModel
from invapp.models.transactions.invoice_model import InvoiceModel
from ..signals import increase_stock_addition,expense_addition
from flask_jwt_extended import jwt_required,get_current_user, get_jwt_identity

blp = Blueprint("Purchasing",__name__,description="Purchasing controls")

@blp.route("/purchase")
class PurchasingView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PurchasingSchema())
    @blp.response(201, InvoiceSchema)
    def post(self, data):
        invoice = InvoiceModel.query.get(data["invoice_id"])
        if not invoice:
            abort(404, message="Invoice does not exists")

        cost = 0
        for item in data["items_list"]:
            existing_item = ItemModel.query.filter_by(item_name=item["item_name"]).first()
            if not existing_item:
                abort(404, message="Item does not exist")
            existing_inv = PurchaseModel.query.filter_by(invoice_id=data["invoice_id"], item_id=existing_item.id).first()
            if existing_inv:
                abort(400, message="Item is already in invoice")
            item_cost = item["item_quantity"] * item["buying_price"]
            item["item_cost"] = item_cost
            cost += item_cost
            line = PurchaseModel(item_id=existing_item.id,item_cost=item_cost , lines_cost=cost,item_quantity=item["item_quantity"], buying_price=item["buying_price"], invoice_id=invoice.id)
            line.save_to_db()
            line.invoice = invoice
            line.items = item

            if invoice.destination_type == "stores":
                increase_stock_addition(item_id=existing_item.id, invoice_id=invoice.id,
                                                 date=invoice.date, quantity=item["item_quantity"], unit_cost=item["buying_price"])

            if invoice.destination_type == "expense":
                expense_addition(item_id=existing_item.id, invoice_id=invoice.id, date=invoice.date, quantity=item["item_quantity"], unit_cost=item["buying_price"])

        if invoice.amount != cost:
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
        if transaction.invoice.accounted != "not_accounted":
            abort(400, message="Invoice is already accounted")
        if transaction.invoice.status != "not paid":
            abort(400, message="Invoice is already paid")
        transaction.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.response(200, PurchasingSchema)
    def get(self, id):
        transaction = PurchaseModel.query.get_or_404(id)
        return transaction

    @jwt_required(fresh=True)
    @blp.arguments(PurchaseUpdateSchema)
    @blp.response(200, InvoiceSchema)
    def patch(self,data, id):
        transaction = PurchaseModel.query.get_or_404(id)
        invoice = transaction.invoice
        if transaction.invoice.accounted != "not_accounted":
            abort(400, message="Invoice is already accounted")
        if transaction.invoice.status != "not paid":
            abort(400, message="Invoice is already paid")
        for line in data:
            item = ItemModel.query.filter_by(item_name=line.get("item_name")).first()
            if not item:
                abort(404, message="Item does not exist")
            transaction.item_id = item.id
            transaction.quantity = line.get("quantity")
            transaction.buying_price = line.get("buying_price")
            transaction.item_cost = line.get("quantity") * line.get("buying_price")
            transaction.lines_cost -= transaction.item_cost
            transaction.update_db()
            transaction.lines_cost += transaction.item_cost
            transaction.update_db()##check logic in frontend

        if invoice.amount != transaction.lines_cost:
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

        invoice = InvoiceModel.query.get(data["invoice_id"])
        return invoice





