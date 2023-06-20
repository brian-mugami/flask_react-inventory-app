from flask.views import MethodView
from flask_smorest import Blueprint,abort
from ..models.masters.accountsmodel import AccountModel
from .. import db
from ..schemas.accountsschema import AccountSchema, AccountUpdateSchema
from flask_jwt_extended import jwt_required

blp = Blueprint("Expense Accounts", __name__, description="Actions on expense accounts")
@blp.route("/expense/account")
class PaymentAccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(AccountSchema)
    @blp.response(201, AccountSchema)
    def post(self, data):
        account = AccountModel.query.filter_by(
            account_name=data["account_name"],
            account_category="Expense Account"
        ).first()
        if account:
            abort(409, message="Account already exists")

        account = AccountModel(account_name=data["account_name"], account_number=data["account_number"],
                               account_description=data["account_description"], account_category="Expense Account")
        account.save_to_db()
        return account

    @jwt_required(fresh=False)
    @blp.response(200, AccountSchema(many=True))
    def get(self):
        accounts = AccountModel.query.filter_by(account_category="Expense Account").all()
        return accounts


@blp.route("/expense/account/<int:id>")
class PaymentAccountView(MethodView):
    @jwt_required(fresh=True)
    def delete(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Expense Account":
            abort(400, message="This is not an expense account")
        account.delete_from_db()

        return {"msg":"deleted"}

    @jwt_required(fresh=True)
    @blp.response(202, AccountSchema)
    def get(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Expense Account":
            abort(400, message="This is not an expense account")
        return account

    @jwt_required(fresh=True)
    @blp.arguments(AccountUpdateSchema)
    def patch(self, data, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Expense Account":
            abort(400, message="This is not an expense account")
        account.account_name = data["account_name"]
        account.account_description = data["account_description"]
        account.account_number = data["account_number"]
        db.session.commit()
        return {"message": "account updated"}, 202