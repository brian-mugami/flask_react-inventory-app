from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..db import db
from ..models import ItemModel
from ..models.transactions.inventory_balances import InventoryBalancesModel
from openpyxl import Workbook,load_workbook
blp = Blueprint("Reports", __name__, description="Report Handling")


@blp.route("/stockholding")
class StockHoldingReport(MethodView):
    def get(self):
        wb = Workbook()
        inventory_summary_query = db.session.query(
            InventoryBalancesModel.item_id,
            func.avg(InventoryBalancesModel.unit_cost).label('average_unit_cost'),
            func.sum(InventoryBalancesModel.quantity).label('total_quantity')
        ).group_by(InventoryBalancesModel.item_id).all()

        ws = wb.active
        ws.title = "stock_holding_report"
        heading = ["Item_name", "unit_cost", "total_quantity"]
        ws.append(heading)
        for balance in inventory_summary_query:
            item = ItemModel.query.get(balance[0])
            print(item.item_name)


