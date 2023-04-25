from sqlalchemy import func
from ..db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from ..models import SupplierModel
from ..models.transactions.supplier_balances_model import SupplierBalanceModel

blp = Blueprint("Supplier balances", __name__, description="Supplier balances actions")

@blp.route("/supplier-balance")
class SupplierBalanceView(MethodView):

    @jwt_required(fresh=True)
    def get(self):
        all_balances = []
        number = 0
        result = db.session.query(SupplierBalanceModel.supplier_id,
                                  func.sum(SupplierBalanceModel.balance).label("supplier_balance"),
                                  SupplierBalanceModel.currency
                                  ).group_by(SupplierBalanceModel.currency, SupplierBalanceModel.supplier_id).all()
        for row in result:
            supplier_id = row.supplier_id
            supplier = SupplierModel.query.get(supplier_id)
            if not supplier:
                abort(404, message="No such supplier is available")
            supplier_name = supplier.supplier_name
            currency = row.currency
            total_amount = row.supplier_balance
            number += 1
            item = {"number": number, "supplier_name": supplier_name, "currency": currency, "total_amount": total_amount}
            all_balances.append(item)

        return {"balances": all_balances}