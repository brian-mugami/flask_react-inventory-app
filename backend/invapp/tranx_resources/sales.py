from flask.views import MethodView
from flask_smorest import Blueprint,abort
from flask_jwt_extended import jwt_required
from ..models.transactions.sales_models import SalesModel
from ..schemas.salesschema import PlainSalesSchema, SalesSchema
from ..models.transactions.inventory_balances import InventoryBalancesModel
from ..signals import sales_accounting_transaction
from ..db import db

blp = Blueprint("Sales", __name__, description="Sales operations")

@blp.route("/sales")
class SalesView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainSalesSchema)
    @blp.response(201,SalesSchema)
    def post(self,data):

        item_in_stock = InventoryBalancesModel.query.filter_by(item_id=data["item_id"]).first()
        if not item_in_stock:
            abort(400, message="Item is not in stock! It might have never been bought!!")

        sale_item_quantity = db.session.query(db.func.sum(InventoryBalancesModel.quantity)).filter_by(item_id=data["item_id"]).scalar()
        if sale_item_quantity <= 0:
            abort(400, message="You do not have enough quantity")

        sale_items = InventoryBalancesModel.query.filter_by(item_id=data["item_id"]).order_by(InventoryBalancesModel.date).all()

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
            sale_added = SalesModel(item_id=data["item_id"],
                                    customer_id=data["customer_id"], currency=data["currency"],
                                    quantity=data["quantity"],
                                    sale_type=data["sale_type"],
                                    selling_price=data["selling_price"])

            sale_added.save_to_db()
            return sale_added
        else:
            abort(400, message="Sale has not be made!!")

    @jwt_required(fresh=True)
    @blp.response(201,SalesSchema(many=True))
    def get(self):
        sales = SalesModel.query.all()
        return sales




