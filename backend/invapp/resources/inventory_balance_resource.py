from flask import jsonify, g
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..db import db
from ..models.masters import ItemModel, AccountModel
from ..models.transactions.inventory_balances import InventoryBalancesModel
from ..schemas.inventory_balance_schema import PlainInventoryBalanceSchema, InventoryBalanceSchema, BalanceSearchSchema
from ..signals import inventory_accounting

blp = Blueprint("Inventory Balances", __name__, description="Inventory Balances Actions")


@blp.route("/balance/search/")
class Invoices(MethodView):

    @jwt_required(fresh=True)
    @blp.arguments(BalanceSearchSchema, location="query")
    def get(self, data):
        name = data.get("item_name", "")
        balances = []
        number = 0
        items = ItemModel.query.filter(ItemModel.item_name.ilike(name)).all()
        if len(items) < 1:
            abort(404, message="No such item")
        for item in items:
            result = db.session.query(
                InventoryBalancesModel.item_id,
                func.sum(InventoryBalancesModel.quantity).label('total_quantity'),
                func.sum(InventoryBalancesModel.quantity * InventoryBalancesModel.unit_cost).label('total_value')
            ).group_by(InventoryBalancesModel.item_id).filter_by(item_id=item.id).all()

            for row in result:
                item_id = row.item_id
                item_name = ItemModel.query.get(item_id).item_name
                total_quantity = row.total_quantity
                total_value = row.total_value
                number += 1
                item = {"number": number, "item_name": item_name, "quantity": total_quantity, "value": total_value}
                balances.append(item)

        return {"balances": balances}


@blp.route("/inventory-balances")
class InventoryBalanceView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainInventoryBalanceSchema)
    @blp.response(201, InventoryBalanceSchema)
    def post(self, data):
        inv_item = ItemModel.query.filter_by(item_name=data.get("item_name")).first()
        account = AccountModel.query.filter_by(account_name=data.get("account_name"),
                                               account_category="Inventory Adjustment Account").first()
        item = ItemModel.query.get(inv_item.id)
        if not item:
            abort(404, message="Item does not exist")
        if not account:
            abort(404, message="No inventory adjustment account found of that name")
        data.pop("item_name")
        data.pop("account_name")
        amount = data.get("quantity", 0) * data.get("unit_cost", 0)
        balance = InventoryBalancesModel(**data, item_id=inv_item.id)
        balance.save_to_db()
        try:
            inventory_accounting(balance_id=balance.id, item_id=balance.item_id, debit_id=item.category.account_id,
                                 credit_id=account.id, amount=amount)
        except:
            balance.delete_from_db()
            abort(500, message="Did not create accounting")
        return balance

    @jwt_required(fresh=True)
    def get(self):
        items = []
        number = 0
        result = db.session.query(
            InventoryBalancesModel.item_id,
            func.sum(InventoryBalancesModel.quantity).label('total_quantity'),
            func.sum(InventoryBalancesModel.quantity * InventoryBalancesModel.unit_cost).label('total_value')
        ).group_by(InventoryBalancesModel.item_id).all()

        for row in result:
            item_id = row.item_id
            item_name = ItemModel.query.get(item_id).item_name
            total_quantity = row.total_quantity
            total_value = row.total_value
            number += 1
            item = {"number": number, "item_name": item_name, "quantity": total_quantity, "value": total_value}
            items.append(item)
        g.items = items
        return ({"balances": items})


@blp.route("/inventory-issue")
class InventoryBalanceView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainInventoryBalanceSchema)
    def post(self, data):
        inv_item = ItemModel.query.filter_by(item_name=data.get("item_name")).first()
        account = AccountModel.query.filter_by(account_name=data.get("account_name"),
                                               account_category="Inventory Adjustment Account").first()
        if not inv_item:
            abort(404, message="Item does not exist")
        if not account:
            abort(404, message="No inventory adjustment account found of that name")
        data.pop("item_name")
        data.pop("account_name")
        sale_item_quantity = db.session.query(db.func.sum(InventoryBalancesModel.quantity)).filter_by(
            item_id=inv_item.id).scalar()
        if sale_item_quantity <= 0:
            abort(400, message="You do not have enough quantity")
        issue_items = InventoryBalancesModel.query.filter_by(item_id=inv_item.id).order_by(
            InventoryBalancesModel.date).all()

        if sale_item_quantity >= data["quantity"]:
            remaining_qty = data["quantity"]
            for item in issue_items:
                if remaining_qty > 0:
                    if item.quantity >= remaining_qty:
                        item.quantity -= remaining_qty
                        remaining_qty = 0
                        item.update_db()
                        amount = data["quantity"] * item.unit_cost
                        try:
                            inventory_accounting(balance_id=item.id, item_id=inv_item.id,
                                                 debit_id=account.id, credit_id=inv_item.category.account_id,
                                                 amount=amount)
                        except:
                            item.delete_from_db()
                            abort(500, message="Did not create accounting")

                    else:
                        remaining_qty -= item.quantity
                        item.quantity = 0
                        item.update_db()
                        amount = data["quantity"] * item.unit_cost
                        try:
                            inventory_accounting(balance_id=item.id, item_id=inv_item.id,
                                                 debit_id=account.id, credit_id=inv_item.category.account_id,
                                                 amount=amount)
                        except:
                            item.delete_from_db()
                            abort(500, message="Did not create accounting")
                else:
                    break

        return ({"balances": "reduced"})
