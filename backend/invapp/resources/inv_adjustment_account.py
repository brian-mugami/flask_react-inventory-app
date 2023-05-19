from flask.views import MethodView
from flask_smorest import Blueprint,abort
from ..models.masters.accountsmodel import AccountModel
from ..schemas.accountsschema import AccountSchema, AccountUpdateSchema
from flask_jwt_extended import jwt_required

blp = Blueprint("Inventory Adjustment Accounts", __name__, description="Actions on inventory adjustment accounts")


@blp.route("/inventory-adjustment/account")
class PurchaseAccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(AccountSchema)
    @blp.response(201, AccountSchema)
    def post(self, data):
        account = AccountModel.query.filter_by(
            account_name=data["account_name"],
            account_category="Inventory Adjustment Account"
        ).first()
        if account:
            abort(409, message="Account already exists")

        account = AccountModel(account_name=data["account_name"], account_number=data["account_number"],
                               account_description=data["account_description"], account_category="Inventory Adjustment Account")

        account.save_to_db()
        return account

    @jwt_required(fresh=False)
    @blp.response(201, AccountSchema(many=True))
    def get(self):
        accounts = AccountModel.query.filter_by(account_category="Inventory Adjustment Account").all()
        return accounts


@blp.route("/inventory-adjustment/account/<int:id>")
class PurchaseAccountView(MethodView):
    @jwt_required(fresh=True)
    def delete(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Inventory Adjustment Account":
            abort(400, message="This is not an Inventory Adjustment Account")
        account.delete_from_db()

        return {"msg":"deleted"}

    @jwt_required(fresh=True)
    @blp.response(202, AccountSchema)
    def get(self, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Inventory Adjustment Account":
            abort(400, message="This is not an Inventory Adjustment Account")
        return account

    @jwt_required(fresh=True)
    @blp.arguments(AccountUpdateSchema)
    def patch(self, data, id):
        account = AccountModel.query.get_or_404(id)
        if account.account_category != "Inventory Adjustment Account":
            abort(400, message="This is not Inventory Adjustment Account")
        account.account_name = data["account_name"]
        account.account_description = data["account_description"]
        account.account_number = data["account_number"]
        account.update_db()

        return {"message": "account updated"}, 202
