import datetime
import traceback

from flask.views import MethodView
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..db import db
from ..models.masters import ItemModel
from ..models.masters.itemmodels import LotModel
from ..schemas.invoice_schema import InvoiceSchema
from ..schemas.purchasingschema import PurchasingSchema, PurchaseUpdateSchema
from flask_smorest import Blueprint, abort
from ..models.transactions.purchasing_models import PurchaseModel
from ..models.transactions.invoice_model import InvoiceModel
from ..signals import increase_stock_addition, expense_addition
from flask_jwt_extended import jwt_required

blp = Blueprint("Purchasing", __name__, description="Purchasing controls")


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
        lot_id = None
        for item in data["items_list"]:
            if len(item["lot"]) < 2:
                pass
            else:
                lot = LotModel.query.filter_by(lot=item["lot"]).first()
                if lot is None:
                    invoice.delete_from_db()
                    abort(404, message="Lot does not exist")
                else:
                    lot_id = lot.id
            existing_item = ItemModel.query.filter_by(item_name=item["item_name"]).first()
            if not existing_item:
                invoice.delete_from_db()
                abort(404, message="Item does not exist")
            existing_inv = PurchaseModel.query.filter_by(invoice_id=data["invoice_id"],
                                                         item_id=existing_item.id).first()
            if existing_inv:
                invoice.delete_from_db()
                abort(400, message="Item is already in invoice")
            item_cost = item["item_quantity"] * item["buying_price"]
            item["item_cost"] = item_cost
            cost += item_cost
            line = PurchaseModel(item_id=existing_item.id, item_cost=item_cost, invoice_amount=invoice.amount,
                                 item_quantity=item["item_quantity"], buying_price=item["buying_price"],
                                 invoice_id=invoice.id, lot_id=lot_id)
            line.save_to_db()
            line.invoice = invoice
            line.items = item

            if invoice.destination_type == "stores":
                increase_stock_addition(item_id=existing_item.id, invoice_id=invoice.id,
                                        date=invoice.date, quantity=item["item_quantity"],
                                        unit_cost=item["buying_price"], lot_id=lot_id)

            if invoice.destination_type == "expense":
                expense_addition(item_id=existing_item.id, invoice_id=invoice.id, date=invoice.date,
                                 quantity=item["item_quantity"], unit_cost=item["buying_price"], lot_id=lot_id)

        if invoice.amount != cost:
            invoice.delete_from_db()
            abort(400, message="Invoice and line amounts do not match, please re-check")
        else:
            invoice.matched_to_lines = "matched"
            invoice.update_db()

        Invoice_lines = InvoiceModel.query.get(data["invoice_id"])
        return Invoice_lines

    @jwt_required(fresh=True)
    @blp.response(200, PurchasingSchema(many=True))
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
    @blp.response(202, InvoiceSchema)
    def put(self, data, id):
        transaction = PurchaseModel.query.get(id)
        invoice = transaction.invoice
        if transaction.invoice.accounted != "not_accounted":
            abort(400, message="Invoice is already accounted")
        if transaction.invoice.status != "not paid":
            abort(400, message="Invoice is already paid")
        lot_id = None
        for line in data["item_list"]:
            if len(line.get("lot")) < 2:
                pass
            else:
                lot = LotModel.query.filter_by(lot=line["lot"]).first()
                if lot is None:
                    abort(404, message="Lot does not exist")
                else:
                    lot_id = lot.id
            item = ItemModel.query.filter_by(item_name=line.get("item_name")).first()
            if not item:
                abort(404, message="Item does not exist")
            if transaction.item_id == item.id and transaction.invoice_id == invoice.id:
                transaction.item_name = line.get("item_name")  # Update item_name
                transaction.item_quantity = line.get("quantity")
                transaction.lot_id = lot_id
                transaction.update_date = datetime.datetime.utcnow()
                transaction.buying_price = line.get("buying_price")
                transaction.invoice_amount = invoice.amount
                cost = transaction.buying_price * transaction.item_quantity
                transaction.item_cost = cost
                transaction.update_db()
            if not transaction:
                try:
                    cost = line.get("buying_price") * line.get("quantity")
                    new_line = PurchaseModel(
                        lot_id=lot_id,
                        item_quantity=line.get("quantity"),
                        buying_price=line.get("buying_price"),
                        item_id=item.id,
                        invoice_id=invoice.id,
                        invoice_amount=invoice.amount,
                        update_date=datetime.datetime.utcnow(),
                        item_cost=cost,
                    )
                    new_line.save_to_db()
                except IntegrityError as e:
                    traceback.print_exc()
                    abort(400, message="Item duplicated in the invoice")
            if invoice.destination_type == "stores":
                increase_stock_addition(
                    item_id=transaction.item_id,
                    invoice_id=invoice.id,
                    date=invoice.date,
                    quantity=transaction.item_quantity,
                    unit_cost=transaction.buying_price,
                    lot_id=lot_id,
                )

            if invoice.destination_type == "expense":
                expense_addition(
                    item_id=transaction.item_id,
                    invoice_id=invoice.id,
                    date=invoice.date,
                    quantity=transaction.item_quantity,
                    unit_cost=transaction.buying_price,
                    lot_id=lot_id,
                )
        result = db.session.query(func.sum(PurchaseModel.item_cost)).filter_by(
            invoice_id=invoice.id
        ).scalar()
        if invoice.amount != result:
            invoice.matched_to_lines = "unmatched"
            invoice.update_db()
        else:
            invoice.matched_to_lines = "matched"
            invoice.update_db()
        invoice = InvoiceModel.query.get(data["invoice_id"])
        return invoice
