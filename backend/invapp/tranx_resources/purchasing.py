import traceback
from flask.views import MethodView
from marshmallow import ValidationError

from ..models import AccountModel, ItemModel, SupplierModel
from ..models.transactions.inventory_balances import InventoryBalancesModel
from ..models.transactions.purchase_accounting_models import PurchaseAccountingModel
from ..schemas.purchasingschema import PurchasingSchema, PurchaseUpdateSchema,PlainPurchasingSchema
from flask_smorest import Blueprint,abort
from invapp.models.transactions.purchasing_models import PurchaseModel
from invapp.models.transactions.invoice_model import InvoiceModel
from ..signals import increase_stock_addition, purchase_accouting_transaction, add_supplier_balance, SignalException, expense_addition
from flask_jwt_extended import jwt_required,get_current_user, get_jwt_identity

blp = Blueprint("Purchasing",__name__,description="Purchasing controls")

@blp.route("/purchase")
class PurchasingView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(PlainPurchasingSchema)
    @blp.response(201, PurchasingSchema)
    def post(self, data):
        transaction = InvoiceModel.query.filter_by(invoice_number=data["invoice_number"], supplier_id=data["supplier_id"]).first()
        if transaction:
            abort(400, message="Invoice already exists")
        supplier = SupplierModel.query.get(data['supplier_id'])
        if not supplier:
            abort(404, message="Supplier not found")
        invoice = InvoiceModel(invoice_number=data["invoice_number"], supplier_id=data["supplier_id"], description=data["description"], currency=data["currency"],date=data["date"],purchase_type=data["purchase_type"],destination_type=data["destination_type"])
        try:
            invoice.save_to_db()
        except Exception as e:
            abort(400, message="Failed to save the invoice")

        new_trx.save_to_db()
        invoice_amount = 0
        for item in data["items"]:
            item = ItemModel.query.get(item["id"])
            if not item:
                raise ValidationError(f'Item with id {item["id"]} does not exist')
            new_trx.item_cost = item["buying_price"] * item["quantity"]
            new_trx.item_id = item.id
            new_trx.quantity = item["quantity"]
            invoice_amount += new_trx.item_cost

        new_trx.update_db()

        if data["purchase_type"] == "cash" and data["destination_type"] == "expense":
            expense_account = AccountModel.query.filter_by(account_name=data["expense_type"],account_type="cash",
                                                            account_category="Expense Account").first()
            supplier_account = new_trx.supplier.account_id
            try:
                expense = expense_addition(items=data["items"],purchase_id=new_trx.id, date=data["date_of_supply"])
                add_supplier_balance(supplier_id=data["supplier_id"], purchase_id=new_trx.id, invoice_amount=invoice_amount,
                                 currency=data["currency"])
                purchase_accouting_transaction(purchase_id=new_trx.id, purchase_account_id=expense_account.id,
                                           supplier_account_id=supplier_account, invoice_amount=invoice_amount,
                                           expense_id=expense)
                return new_trx
            except SignalException as e:
                abort(500, message=f"Failed to add expense please try again: {str(e)}")
                new_trx.delete_from_db()

        if data["purchase_type"] == "credit" and data["destination_type"] == "expense":
            expense_account = AccountModel.query.filter_by(account_type="credit",account_name=data["expense_type"],
                                                            account_category="Expense Account", ).first()
            supplier_account = new_trx.supplier.account_id
            try:
                expense = expense_addition(items=data["items"],purchase_id=new_trx.id, date=data["date_of_supply"])
                add_supplier_balance(supplier_id=data["supplier_id"], purchase_id=new_trx.id, invoice_amount=invoice_amount,
                                 currency=data["currency"])
                purchase_accouting_transaction(purchase_id=new_trx.id, purchase_account_id=expense_account.id,
                                           supplier_account_id=supplier_account, invoice_amount=invoice_amount,
                                           expense_id=expense)
                return new_trx
            except SignalException as e:
                abort(500, message=f"Failed to add expense please try again: {str(e)}")
                new_trx.delete_from_db()


        if data["purchase_type"] == "cash" and data["destination_type"] == "stores":
            """cash purchase"""
            try:
                purchase_account = AccountModel.query.filter_by(account_type="cash", account_category="Purchase Account").first()
                supplier_account = new_trx.supplier.account_id
                try:
                    result = increase_stock_addition(items=data["items"], purchase_id=new_trx.id, date=data["date_of_supply"])
                    purchase_accouting_transaction(purchase_id=new_trx.id,purchase_account_id=purchase_account.id,supplier_account_id=supplier_account,invoice_amount=invoice_amount, inv_id=result)
                    add_supplier_balance(supplier_id=data["supplier_id"],purchase_id=new_trx.id, invoice_amount=invoice_amount, currency=data["currency"])
                except SignalException as e:
                    abort(500, message=f"Failed to add to store, please try again: {str(e)}")
                    new_trx.delete_from_db()
                return new_trx
            except:
                traceback.print_exc()
                abort(500, message="Did not save to the db")

        if  data["purchase_type"] == "cash" and data["destination_type"] == "stores":
            try:
                purchase_account = AccountModel.query.filter_by(account_type="credit", account_category="Purchase Account").first()
                supplier_account = new_trx.supplier.account_id
                try:
                    result = increase_stock_addition(items=data["items"], purchase_id=new_trx.id, date=data["date_of_supply"])
                    purchase_accouting_transaction(purchase_id=new_trx.id,purchase_account_id=purchase_account.id,supplier_account_id=supplier_account,invoice_amount=invoice_amount, inv_id=result)
                    add_supplier_balance(supplier_id=data["supplier_id"],purchase_id=new_trx.id, invoice_amount=invoice_amount, currency=data["currency"])
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







