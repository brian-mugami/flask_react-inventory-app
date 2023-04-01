import traceback
from flask.views import MethodView
from ..models import AccountModel
from ..models.transactions.inventory_balances import InventoryBalancesModel
from ..models.transactions.purchase_accounting_models import PurchaseAccountingModel
from ..schemas.purchasingschema import PurchasingSchema, PurchaseUpdateSchema
from flask_smorest import Blueprint,abort
from invapp.models.transactions.purchasing_models import PurchaseModel
from ..signals import increase_stock_addition, purchase_accouting_transaction, add_supplier_balance, SignalException, expense_addition
from flask_jwt_extended import jwt_required,get_current_user, get_jwt_identity

blp = Blueprint("Purchasing",__name__,description="Purchasing controls")

@blp.route("/purchase")
class PurchasingView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PurchasingSchema)
    @blp.response(201, PurchasingSchema)
    def post(self, data):
        transaction = PurchaseModel.query.filter_by(invoice_number=data["invoice_number"], supplier_id=data["supplier_id"], item_id=data["item_id"]).first()
        if transaction:
            abort(400, message="Invoice already exists")
        new_trx = PurchaseModel(invoice_number=data["invoice_number"], currency=data["currency"], item_id=data["item_id"],quantity=data["quantity"],
                                destination_type=data["destination_type"],supplier_id=data["supplier_id"], date_of_supply=data["date_of_supply"], buying_price=data["buying_price"], description=data["description"], purchase_type=data["purchase_type"])

        if data["purchase_type"] == "cash" and data["destination_type"] == "expense":
            new_trx.save_to_db()
            expense_account = AccountModel.query.filter_by(account_name=data["expense_type"],account_type="cash",
                                                            account_category="Expense Account").first()
            supplier_account = new_trx.supplier.account_id
            item_cost = new_trx.buying_price
            quantity = new_trx.quantity
            amount = quantity * item_cost
            try:
                expense = expense_addition(item_id=data["item_id"],purchase_id=new_trx.id,cost=data["buying_price"], quantity=data["quantity"], date=data["date_of_supply"])
                add_supplier_balance(supplier_id=data["supplier_id"], purchase_id=new_trx.id, invoice_amount=amount,
                                 currency=data["currency"])
                purchase_accouting_transaction(purchase_id=new_trx.id, purchase_account_id=expense_account.id,
                                           supplier_account_id=supplier_account, cost=item_cost, quantity=quantity,
                                           expense_id=expense)
                return new_trx
            except SignalException as e:
                abort(500, message=f"Failed to add expense please try again: {str(e)}")
                new_trx.delete_from_db()

        if data["purchase_type"] == "credit" and data["destination_type"] == "expense":
            new_trx.save_to_db()
            expense_account = AccountModel.query.filter_by(account_type="credit",account_name=data["expense_type"],
                                                            account_category="Expense Account", ).first()
            supplier_account = new_trx.supplier.account_id
            item_cost = new_trx.buying_price
            quantity = new_trx.quantity
            amount = quantity * item_cost
            try:
                expense = expense_addition(item_id=data["item_id"],purchase_id=new_trx.id,cost=data["buying_price"], quantity=data["quantity"], date=data["date_of_supply"])
                add_supplier_balance(supplier_id=data["supplier_id"], purchase_id=new_trx.id, invoice_amount=amount,
                                 currency=data["currency"])
                purchase_accouting_transaction(purchase_id=new_trx.id, purchase_account_id=expense_account.id,
                                           supplier_account_id=supplier_account, cost=item_cost, quantity=quantity,
                                           expense_id=expense)
                return new_trx
            except SignalException as e:
                abort(500, message=f"Failed to add expense please try again: {str(e)}")
                new_trx.delete_from_db()


        if data["purchase_type"] == "cash" and data["destination_type"] == "stores":
            """cash purchase"""
            try:
                new_trx.save_to_db()
                purchase_account = AccountModel.query.filter_by(account_type="cash", account_category="Purchase Account").first()
                supplier_account = new_trx.supplier.account_id
                item_cost = new_trx.buying_price
                quantity = new_trx.quantity
                amount = quantity * item_cost
                try:
                    result = increase_stock_addition(data["item_id"], purchase_id=new_trx.id,cost=data["buying_price"], quantity=data["quantity"], date=data["date_of_supply"])
                    purchase_accouting_transaction(purchase_id=new_trx.id,purchase_account_id=purchase_account.id,supplier_account_id=supplier_account,cost=item_cost, quantity=quantity, inv_id=result)
                    add_supplier_balance(supplier_id=data["supplier_id"],purchase_id=new_trx.id, invoice_amount=amount, currency=data["currency"])
                except SignalException as e:
                    abort(500, message=f"Failed to add to store, please try again: {str(e)}")
                    new_trx.delete_from_db()
                return new_trx
            except:
                traceback.print_exc()
                abort(500, message="Did not save to the db")

        if  data["purchase_type"] == "cash" and data["destination_type"] == "stores":
            try:
                new_trx.save_to_db()
                purchase_account = AccountModel.query.filter_by(account_type="credit", account_category="Purchase Account").first()
                supplier_account = new_trx.supplier.account_id
                item_cost = new_trx.buying_price
                quantity = new_trx.quantity
                amount = quantity*item_cost
                try:
                    result = increase_stock_addition(data["item_id"],purchase_id=new_trx.id, cost=data["buying_price"], quantity=data["quantity"], date=data["date_of_supply"])
                    purchase_accouting_transaction(purchase_id=new_trx.id,purchase_account_id=purchase_account.id,supplier_account_id=supplier_account,cost=item_cost, quantity=quantity, inv_id=result)
                    add_supplier_balance(supplier_id=data["supplier_id"],purchase_id=new_trx.id, invoice_amount=amount, currency=data["currency"])
                except:
                    abort(500, message="Failed to add to store, please try again")
                    new_trx.delete_from_db()
                return new_trx
            except:
                traceback.print_exc()
                abort(500, message=f"Did not save to the db")

    @jwt_required(fresh=True)
    @blp.response(200,PurchasingSchema(many=True))
    def get(self):
        purchases = PurchaseModel.query.all()
        return purchases

@blp.route("/purchase/<int:id>")
class PurchaseManipulateView(MethodView):
    @jwt_required(fresh=True)
    def delete(self, id):
        transaction = PurchaseModel.query.get_or_404(id)
        transaction.delete_from_db()
        return {"message": "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.response(200, PurchasingSchema)
    def get(self, id):
        transaction = PurchaseModel.query.get_or_404(id)
        return transaction

    @jwt_required(fresh=True)
    @blp.arguments(PurchaseUpdateSchema)
    @blp.response(200, PurchasingSchema)
    def patch(self,data, id):
        transaction = PurchaseModel.query.get_or_404(id)

        transaction.invoice_number = data["invoice_number"]
        transaction.description = data["description"]
        transaction.buying_price = data["buying_price"]
        transaction.currency = data["currency"]
        transaction.purchase_type = data["purchase_type"]
        transaction.update_date = data["update_date"]
        transaction.supplier_id = data["supplier_id"]
        transaction.item_id = data["item_id"]
        transaction.destination_type = data["destination_type"]

        if data["purchase_type"] == "cash" and data["destination_type"] == "stores":
            """cash purchase"""
            try:
                transaction.update_db()
                purchase_account = AccountModel.query.filter_by(account_type="cash", account_category="Purchase Account").first()
                supplier_account = transaction.supplier.account_id
                item_cost = transaction.buying_price
                quantity = transaction.quantity
                amount = quantity * item_cost
                try:
                    accounting_trx = PurchaseAccountingModel.query.filter_by(purchase_id=transaction.id).first()
                    balances_trx = InventoryBalancesModel.query.filter_by(purchase_id=transaction.id).first()
                    if accounting_trx and balances_trx:
                        result = increase_stock_addition(transaction.item_id, purchase_id=transaction.id,cost=transaction.buying_price, quantity=transaction.quantity, date=data["date_of_supply"])
                        purchase_accouting_transaction(purchase_id=transaction.id,purchase_account_id=purchase_account.id,supplier_account_id=supplier_account,cost=item_cost, quantity=quantity, inv_id=result.id)
                        add_supplier_balance(supplier_id=data["supplier_id"], amount=amount,
                                                       currency=data["currency"], purchase_id=transaction.id)
                        return transaction
                except SignalException as e:
                    abort(500, message=f"Failed to update to store, please try again: {str(e)}")
            except:
                traceback.print_exc()
                abort(500, message="Did not save to the db")
        if data["purchase_type"] == "credit" and data["destination_type"] == "stores":
            try:
                transaction.update_db()
                purchase_account = AccountModel.query.filter_by(account_type="credit", account_category="Purchase Account").first()
                supplier_account = transaction.supplier.account_id
                item_cost = transaction.buying_price
                quantity = transaction.quantity
                amount = item_cost * quantity
                try:
                    result = increase_stock_addition(data["item_id"],purchase_id=transaction.id, cost=data["buying_price"], quantity=data["quantity"], date=data["date_of_supply"])
                    purchase_accouting_transaction(purchase_account_id=purchase_account.id,purchase_id=transaction.id,supplier_account_id=supplier_account,cost=item_cost, quantity=quantity, inv_id=result.id)
                    add_supplier_balance(supplier_id=data["supplier_id"], amount=amount,
                                                   currency=data["currency"], purchase_id=transaction.id)
                    return transaction
                except SignalException as e:
                    abort(500, message=f"Failed to update to store, please try again:{str(e)}")
            except:
                traceback.print_exc()
                abort(500, message=f"Did not save to the db")

        if data["purchase_type"] == "cash" and data["destination_type"] == "expense":
            try:
                transaction.update_db()
                expense_account = AccountModel.query.filter_by(account_name=data["expense_type"], account_type="cash",
                                                               account_category="Expense Account").first()
                supplier_account = transaction.supplier.account_id
                item_cost = transaction.buying_price
                quantity = transaction.quantity
                amount = quantity * item_cost
                try:
                    expense = expense_addition(item_id=data["item_id"], purchase_id=transaction.id,
                                               cost=data["buying_price"], quantity=data["quantity"],
                                               date=data["date_of_supply"])
                    add_supplier_balance(supplier_id=data["supplier_id"], purchase_id=transaction.id, invoice_amount=amount,
                                         currency=data["currency"])
                    purchase_accouting_transaction(purchase_id=transaction.id, purchase_account_id=expense_account.id,
                                                   supplier_account_id=supplier_account, cost=item_cost,
                                                   quantity=quantity,
                                                   expense_id=expense)
                    return transaction
                except SignalException as e:
                    abort(500, message=f"Failed to add expense please try again: {str(e)}")
            except:
                traceback.print_exc()
                abort(500, message=f"Did not save to the db")

        if data["purchase_type"] == "credit" and data["destination_type"] == "expense":
            try:
                transaction.update_db()
                expense_account = AccountModel.query.filter_by(account_name=data["expense_type"], account_type="credit",
                                                               account_category="Expense Account").first()
                supplier_account = transaction.supplier.account_id
                item_cost = transaction.buying_price
                quantity = transaction.quantity
                amount = quantity * item_cost
                try:
                    expense = expense_addition(item_id=data["item_id"], purchase_id=transaction.id,
                                               cost=data["buying_price"], quantity=data["quantity"],
                                               date=data["date_of_supply"])
                    add_supplier_balance(supplier_id=data["supplier_id"], purchase_id=transaction.id,
                                         invoice_amount=amount,
                                         currency=data["currency"])
                    purchase_accouting_transaction(purchase_id=transaction.id, purchase_account_id=expense_account.id,
                                                   supplier_account_id=supplier_account, cost=item_cost,
                                                   quantity=quantity,
                                                   expense_id=expense)
                    return transaction
                except SignalException as e:
                    abort(500, message=f"Failed to add expense please try again: {str(e)}")
            except:
                traceback.print_exc()
                abort(500, message=f"Did not save to the db")







