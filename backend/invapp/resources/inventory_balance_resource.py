from flask import jsonify, g
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..db import db
from invapp.models import ItemModel
from invapp.models.transactions.inventory_balances import InventoryBalancesModel
from invapp.schemas.inventory_balance_schema import PlainInventoryBalanceSchema, InventoryBalanceSchema, BalanceSearchSchema

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
        g.item_id = inv_item.id
        item = ItemModel.query.get(inv_item.id)
        if not item:
            abort(404, message="Item does not exist")
        data.pop("item_name")
        balance = InventoryBalancesModel(**data, item_id=inv_item.id)
        balance.save_to_db()
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
            item = {"number":number ,"item_name": item_name,"quantity": total_quantity, "value":total_value}
            items.append(item)
        g.items = items
        return ({"balances": items})

@blp.route("/inventory-issue")
class InventoryBalanceView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainInventoryBalanceSchema)
    def post(self, data):
        inv_item = ItemModel.query.filter_by(item_name=data.get("item_name")).first()
        g.item_id = inv_item.id
        item = ItemModel.query.get(inv_item.id)
        if not item:
            abort(404, message="Item does not exist")
        data.pop("item_name")
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
                    else:
                        remaining_qty -= item.quantity
                        item.quantity = 0
                        item.update_db()
                else:
                    break
        return ({"balances": "reduced"})


