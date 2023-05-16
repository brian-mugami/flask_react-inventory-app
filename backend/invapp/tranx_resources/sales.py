import datetime
import traceback

from flask.views import MethodView
from flask_smorest import Blueprint,abort
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..models.masters import AccountModel, ItemModel
from ..models.transactions.receipt_model import ReceiptModel
from ..models.transactions.sales_models import SalesModel
from ..schemas.receiptschema import ReceiptSchema
from ..schemas.salesschema import PlainSalesSchema, SalesSchema
from ..models.transactions.inventory_balances import InventoryBalancesModel
from ..signals import sales_accounting_transaction, add_customer_balance, SignalException
from ..db import db
blp = Blueprint("Sales", __name__, description="Sales operations")

@blp.route("/sales")
class SalesView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainSalesSchema)
    @blp.response(201,ReceiptSchema)
    def post(self, data):
        receipt = ReceiptModel.query.get(data["receipt_id"])
        if not receipt:
            abort(404, message="receipt not found")

        cost = 0
        for receipt_item in data["item_list"]:
            in_receipt_item = ItemModel.query.filter_by(item_name=receipt_item["item_name"]).first()
            if not in_receipt_item:
                abort(404, message=f"{data['item_name']} not found")
            repeated_item = SalesModel.query.filter_by(item_id=in_receipt_item.id, receipt_id=receipt.id).first()
            if repeated_item:
                abort(400, message=f"{in_receipt_item.item_name} is in the receipt twice")
            item_in_stock = InventoryBalancesModel.query.filter_by(item_id=in_receipt_item.id).first()
            if not item_in_stock:
                abort(400, message=f"{in_receipt_item.item_name} is not in stock! It might have never been bought!!")

            sale_item_quantity = db.session.query(db.func.sum(InventoryBalancesModel.quantity)).filter_by(
                item_id=in_receipt_item.id).scalar()
            if sale_item_quantity <= 0:
                abort(400, message=f"{in_receipt_item.item_name} has insufficient quantity")

            sale_items = InventoryBalancesModel.query.filter_by(item_id=in_receipt_item.id).order_by(
                InventoryBalancesModel.date).all()

            if sale_item_quantity >= receipt_item["quantity"]:
                remaining_qty = receipt_item["quantity"]
                for item in sale_items:
                    if remaining_qty > 0:
                        if item.quantity >= remaining_qty:
                            item.quantity -= remaining_qty
                            remaining_qty = 0
                            item_cost = receipt_item["quantity"] * receipt_item["selling_price"]

                        else:
                            remaining_qty -= item.quantity
                            item.quantity = 0
                            item_cost = receipt_item["quantity"] * receipt_item["selling_price"]

                    else:
                        break

                # Add sale item to Sales model
                sale_item = SalesModel(item_id=in_receipt_item.id,
                                       receipt_id=receipt.id,
                                       quantity=receipt_item["quantity"],
                                       selling_price=receipt_item["selling_price"],
                                       item_cost=item_cost)
                cost += item_cost
                sale_item.save_to_db()

            else:
                abort(400, message="Sale has not be made, not enough quantity!!")
        receipt.amount = cost
        receipt.update_db()

        if receipt.sale_type == "cash":
            """cash sale"""
            cash_account = AccountModel.query.filter_by(account_type="cash",
                                                        account_category="Sale Account").first()
            customer_account = receipt.customer.account_id
            amount = receipt.amount
            customer_id = receipt.customer.id
            try:
                add_customer_balance(customer_id=customer_id, receipt_id=receipt.id, receipt_amount=amount)
                sales_accounting_transaction(sales_account_id=cash_account.id, receipt_id=receipt.id,
                                             customer_account_id=customer_account, amount=amount)
                receipt = ReceiptModel.query.get(receipt.id)
                receipt.accounted_status = "fully_accounted"
                receipt.update_db()
                return receipt
            except SignalException as e:
                traceback.print_exc()
                abort(500, message="Server error when accounting")
        else:
            cash_account = AccountModel.query.filter_by(account_type="credit",
                                                        account_category="Sale Account").first()
            customer_account = receipt.customer.account_id
            amount = receipt.amount
            customer_id = receipt.customer.id
            try:
                add_customer_balance(customer_id=customer_id, receipt_id=receipt.id, receipt_amount=amount)
                sales_accounting_transaction(sales_account_id=cash_account.id, receipt_id=receipt.id,
                                             customer_account_id=customer_account, amount=amount)
                receipt = ReceiptModel.query.get(receipt.id)
                receipt.accounted_status = "fully_accounted"
                receipt.update_db()
                return receipt
            except SignalException as e:
                traceback.print_exc()
                abort(500, message="Server error when accounting")

    @jwt_required(fresh=True)
    @blp.response(201,SalesSchema(many=True))
    def get(self):
        sales = SalesModel.query.all()
        return sales

@blp.route("/sales/<int:id>")
class SalesMethodView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, SalesSchema(many=True))
    def get(self, id):
        sale = SalesModel.query.get_or_404(id)
        return sale

    @jwt_required(fresh=True)
    def delete(self, id):
        transaction = SalesModel.query.get_or_404(id)
        transaction.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.arguments(SalesSchema)
    @blp.response(200, SalesSchema)
    def put(self,data, id):
        transaction = SalesModel.query.get_or_404(id)
        receipt = transaction.receipt
        if receipt.status != "not paid":
            abort(400, message="This receipt cant be edited as payment has began")
        for line in data.get("item_list"):
            item = ItemModel.query.filter_by(item_name=line.get("item_name")).first()
            if not item:
                abort(404, message="Item does not exist")
            if transaction.item_id == item.id and transaction.receipt_id == receipt.id:

                transaction.item_quantity = line.get("quantity")
                transaction.selling_price = line.get("selling_price")
                transaction.item_cost = transaction.selling_price * transaction.quantity
                transaction.update_db()

                item_in_stock = InventoryBalancesModel.query.filter_by(item_id=item.id).first()
                if not item_in_stock:
                    abort(400, message="Item is not in stock! It might have never been bought!!")

                sale_item_quantity = db.session.query(db.func.sum(InventoryBalancesModel.quantity)).filter_by(
                    item_id=item.id).scalar()
                if sale_item_quantity <= 0:
                    abort(400, message="You do not have enough quantity")

                sale_items = InventoryBalancesModel.query.filter_by(item_id=item.id).order_by(
                    InventoryBalancesModel.date).all()

                if sale_item_quantity >= line["quantity"]:
                    remaining_qty = line["quantity"]
                    for item in sale_items:
                        if remaining_qty > 0:
                            if item.quantity >= remaining_qty:
                                item.quantity -= remaining_qty
                                remaining_qty = 0
                            else:
                                remaining_qty -= item.quantity
                                item.quantity = 0
                        else:
                            break
        result = db.session.query(func.sum(SalesModel.item_cost)).filter_by(receipt_id=receipt.id).scalar()

        receipt.amount = result
        receipt.update_db()

        if receipt.sale_type == "cash":
            """cash sale"""
            cash_account = AccountModel.query.filter_by(account_type="cash",
                                                        account_category="Sale Account").first()
            customer_account = receipt.customer.account_id
            customer_id = receipt.customer.id
            try:
                add_customer_balance(customer_id=customer_id, receipt_id=receipt.id, receipt_amount=result)
                sales_accounting_transaction(sales_account_id=cash_account.id, receipt_id=receipt.id,
                                             customer_account_id=customer_account, amount=result)
                receipt = ReceiptModel.query.get(receipt.id)
                receipt.accounted_status = "fully_accounted"
                receipt.update_db()
                return receipt
            except SignalException as e:
                traceback.print_exc()
                abort(500, message="Server error when accounting")
        else:
            cash_account = AccountModel.query.filter_by(account_type="credit",
                                                        account_category="Sale Account").first()
            customer_account = receipt.customer.account_id
            customer_id = receipt.customer.id
            try:
                add_customer_balance(customer_id=customer_id, receipt_id=receipt.id, receipt_amount=result)
                sales_accounting_transaction(sales_account_id=cash_account.id, receipt_id=receipt.id,
                                             customer_account_id=customer_account, amount=result)
                receipt = ReceiptModel.query.get(receipt.id)
                receipt.accounted_status = "fully_accounted"
                receipt.update_db()
                return receipt
            except SignalException as e:
                traceback.print_exc()
                abort(500, message="Server error when accounting")









