import datetime

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from ..models.transactions.bank_balances_model import BankBalanceModel
from ..schemas.bank_balance_schema import PlainBankBalanceSchema,BankBalanceSchema
from flask_jwt_extended import jwt_required

blp = Blueprint("bank_balances", __name__, description="Bank balance actions")

@blp.route("/bank/balance")
class BankBalanceView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, BankBalanceSchema(many=True))
    def get(self):
        balances = BankBalanceModel.query.all()
        return balances

    @jwt_required(fresh=True)
    @blp.arguments(PlainBankBalanceSchema)
    @blp.response(201, BankBalanceSchema)
    def post(self, data):
        balance = BankBalanceModel.query.filter_by(invoice_id=data["invoice_id"], receipt_id=data["receipt_id"], bank_account_id=data["bank_account_id"]).first()
        if balance:
            abort(400, message="This already exists")
        new_balance = BankBalanceModel(**data)
        new_balance.save_to_db()
        return new_balance

@blp.route("/bank/balance/<int:id>")
class BankMethodView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, BankBalanceSchema)
    def get(self, id):
        balance = BankBalanceModel.query.get_or_404(id)
        return balance

    @jwt_required(fresh=True)
    def delete(self, id):
        balance = BankBalanceModel.query.get_or_404(id)
        balance.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.arguments(PlainBankBalanceSchema)
    @blp.response(201, BankBalanceSchema)
    def patch(self,data, id):
        balance = BankBalanceModel.query.get_or_404(id)
        balance.amount = data["amount"]
        balance.update_date = datetime.datetime.utcnow()
        balance.invoice_id = data["invoice_id"]
        balance.receipt_id = data["receipt_id"]
        balance.bank_account_id = data["balance_account_id"]
        balance.currency = data["currency"]
        balance.update_db()

        return balance




