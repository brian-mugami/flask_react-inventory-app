import traceback
from flask import jsonify, current_app, send_file, g
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..models import ItemModel
from ..models.transactions.expenses_model import ExpensesModel
from ..db import db

blp = Blueprint("Expenses", __name__, description="Sorting expenses")

@blp.route("/expenses")
class ExpensesView(MethodView):
    def get(self):
        items = []
        number = 0
        result = db.session.query(
            ExpensesModel.item_id,
            func.sum(ExpensesModel.quantity).label('total_quantity'),
            func.sum(ExpensesModel.quantity * ExpensesModel.unit_cost).label('total_value')
        ).group_by(ExpensesModel.item_id).all()

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