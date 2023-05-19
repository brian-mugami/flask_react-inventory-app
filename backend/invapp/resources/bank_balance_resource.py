import datetime

from sqlalchemy import func

from ..db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..models.masters import AccountModel
from ..models.transactions.bank_balances_model import BankBalanceModel
from ..schemas.bank_balance_schema import PlainBankBalanceSchema,BankBalanceSchema
from flask_jwt_extended import jwt_required

blp = Blueprint("bank_balances", __name__, description="Bank balance actions")

@blp.route("/bank/balance")
class BankBalanceView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        all_bank_balances = []
        number = 0
        result = db.session.query(BankBalanceModel.bank_account_id,
                                  func.sum(BankBalanceModel.amount).label("Total_Bank_Balance"),
                                  BankBalanceModel.currency
                                  ).group_by(BankBalanceModel.currency, BankBalanceModel.bank_account_id).all()
        for row in result:
            bank_id = row.bank_account_id
            account = AccountModel.query.get(bank_id)
            if not account:
                abort(404, message="No such bank account is available")
            account_name = account.account_name
            currency = row.currency
            total_amount = row.Total_Bank_Balance
            number += 1
            item = {"number": number, "account_name": account_name, "currency": currency, "total_amount":total_amount}
            all_bank_balances.append(item)


        return {"balances": all_bank_balances}


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




