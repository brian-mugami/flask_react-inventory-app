import datetime
import traceback

from flask.views import MethodView
from flask_smorest import Blueprint,abort
from flask_jwt_extended import jwt_required
from ..models import AccountModel
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

        total_cost = 0
        cost = 0
        for receipt_item in data["item_list"]:
            repeated_item = SalesModel.query.filter_by(item_id=receipt_item["item_id"], receipt_id=receipt.id).first()
            if repeated_item:
                abort(400, message="Item is already in the receipt")
            item_in_stock = InventoryBalancesModel.query.filter_by(item_id=receipt_item["item_id"]).first()
            if not item_in_stock:
                abort(400, message="Item is not in stock! It might have never been bought!!")

            sale_item_quantity = db.session.query(db.func.sum(InventoryBalancesModel.quantity)).filter_by(
                item_id=receipt_item["item_id"]).scalar()
            if sale_item_quantity <= 0:
                abort(400, message="You do not have enough quantity")

            sale_items = InventoryBalancesModel.query.filter_by(item_id=receipt_item["item_id"]).order_by(
                InventoryBalancesModel.date).all()

            if sale_item_quantity >= receipt_item["quantity"]:
                remaining_qty = receipt_item["quantity"]
                for item in sale_items:
                    if remaining_qty > 0:
                        if item.quantity >= remaining_qty:
                            item.quantity -= remaining_qty
                            remaining_qty = 0
                            item_cost = receipt_item["quantity"] * receipt_item["selling_price"]
                            cost = item_cost
                            total_cost += item_cost
                        else:
                            remaining_qty -= item.quantity
                            item.quantity = 0
                            item_cost = receipt_item["quantity"] * receipt_item["selling_price"]
                            cost = item_cost
                            total_cost += item_cost
                    else:
                        break

                # Add sale item to Sales model
                sale_item = SalesModel(item_id=receipt_item["item_id"],
                                       receipt_id=receipt.id,
                                       quantity=receipt_item["quantity"],
                                       selling_price=receipt_item["selling_price"],
                                       item_cost=cost)
                sale_item.save_to_db()

            else:
                abort(400, message="Sale has not be made, not enough quantity!!")

        # Update receipt amount
        receipt.amount = total_cost
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
                return receipt
            except SignalException as e:
                traceback.print_exc()
                return {"message": f"{str(e)}"}
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
                return receipt
            except SignalException as e:
                traceback.print_exc()
                return {"message": f"{str(e)}"}

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
    def patch(self,data, id):
        transaction = SalesModel.query.get_or_404(id)
        if transaction:
            transaction.item_id = data["item_id"]
            transaction.customer_id = data["customer_id"]
            transaction.description = data["description"]
            transaction.quantity = data["quantity"]
            transaction.selling_price = data["selling_price"]
            transaction.currency = data["currency"]
            transaction.update_date = datetime.datetime.utcnow()
            transaction.sale_type = data["sale_type"]

            item_in_stock = InventoryBalancesModel.query.filter_by(item_id=data["item_id"]).first()
            if not item_in_stock:
                abort(400, message="Item is not in stock! It might have never been bought!!")

            sale_item_quantity = db.session.query(db.func.sum(InventoryBalancesModel.quantity)).filter_by(
                item_id=data["item_id"]).scalar()
            if sale_item_quantity <= 0:
                abort(400, message="You do not have enough quantity")

            sale_items = InventoryBalancesModel.query.filter_by(item_id=data["item_id"]).order_by(
                InventoryBalancesModel.date).all()

            if sale_item_quantity >= data["quantity"]:
                remaining_qty = data["quantity"]
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
                if data["sale_type"] == "cash":
                    """cash sale"""
                    transaction.update_db()
                    cash_account = AccountModel.query.filter_by(account_type="cash",
                                                                account_category="Sale Account").first()
                    customer_account = transaction.customer.account_id
                    selling_price = transaction.selling_price
                    quantity = transaction.quantity
                    customer_id = transaction.customer.id
                    try:
                        sales_accounting_transaction(sales_account_id=cash_account.id, sale_id=transaction.id,
                                                     customer_account_id=customer_account, selling_price=selling_price,
                                                     quantity=quantity)
                        add_customer_balance(customer_id=customer_id, sale_id=transaction.id,
                                             receipt_amount=transaction.amount)
                    except:
                        traceback.print_exc()
                        return {"message": "Could not create accounting"}
                    return transaction
                else:
                    transaction.save_to_db()
                    cash_account = AccountModel.query.filter_by(account_type="credit",
                                                                account_category="Sale Account").first()
                    customer_account = transaction.customer.account_id
                    selling_price = transaction.selling_price
                    quantity = transaction.quantity
                    customer_id = transaction.customer.id
                    try:
                        sales_accounting_transaction(sales_account_id=cash_account.id, sale_id=transaction.id,
                                                     customer_account_id=customer_account, selling_price=selling_price,
                                                     quantity=quantity)
                        add_customer_balance(customer_id=customer_id, sale_id=transaction.id,
                                             receipt_amount=transaction.amount)
                    except:
                        traceback.print_exc()
                        return {"message": "Could not create accounting"}
                    return transaction
            else:
                abort(400, message="Sale has not be made, not enough quantity!!")









