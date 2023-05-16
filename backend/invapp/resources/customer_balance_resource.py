from sqlalchemy import func
from ..db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from ..models.masters import CustomerModel
from ..models.transactions.customer_balances_model import CustomerBalanceModel

blp = Blueprint("Customer balances", __name__, description="Customer balance actions")

@blp.route("/customer-balance")
class CustomerBalanceView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        all_balances = []
        number = 0
        result = db.session.query(CustomerBalanceModel.customer_id,
                                  func.sum(CustomerBalanceModel.balance).label("customer_balance"),
                                  CustomerBalanceModel.currency
                                  ).group_by(CustomerBalanceModel.currency, CustomerBalanceModel.customer_id).all()
        for row in result:
            customer_id = row.customer_id
            customer = CustomerModel.query.get(customer_id)
            if not customer:
                abort(404, message="No such customer is available")
            customer_name = customer.customer_name
            currency = row.currency
            total_amount = row.customer_balance
            number += 1
            item = {"number": number, "customer_name": customer_name, "currency": currency,
                    "total_amount": total_amount}
            all_balances.append(item)

        return {"balances": all_balances}