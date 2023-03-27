import datetime

from blinker import signal

from invapp.models.transactions.inventory_balances import InventoryBalancesModel
from invapp.models.transactions.accountingmodels import PurchaseAccountingModel
from flask import jsonify

send_data = signal('send-data')
purchase_account = signal('purchase_account')
pay_supplier = signal("pay-supplier")
class SignalException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

@send_data.connect
def increase_stock_addition(item_id: int,purchase_id:int, cost: float, quantity: int, date: str=None):
    item = InventoryBalancesModel.query.filter_by(purchase_id=purchase_id, item_id=item_id).first()
    if item:
        item.cost = cost
        item.quantity = quantity
        item.update_date = datetime.datetime.utcnow()
        item.save_to_db()
        return item.id
    onhand_item = InventoryBalancesModel(item_id=item_id, purchase_id=purchase_id,cost=cost, quantity=quantity, date=date)
    try:
        onhand_item.save_to_db()
        return onhand_item.id
    except:
        raise SignalException("Failed to add to stores")


@purchase_account.connect
def purchase_accouting_transaction(purchase_account_id: int, purchase_id: int,supplier_account_id: int, cost: float, quantity: int, inv_id: int):
    amount = cost * quantity
    existing_accounting = PurchaseAccountingModel.query.filter_by(purchase_id=purchase_id, inventory_id=inv_id).first()
    if existing_accounting:
        existing_accounting.supplier_account_id = supplier_account_id
        existing_accounting.purchase_account_id = purchase_account_id
        existing_accounting.credit_amount = -amount
        existing_accounting.debit_amount = amount
        existing_accounting.update_date = datetime.datetime.utcnow()
        existing_accounting.save_to_db()
        return jsonify({"message": "updated"})
    purchase_account = PurchaseAccountingModel(credit_account_id=supplier_account_id,debit_account_id=purchase_account_id,
                                          debit_amount=amount, credit_amount=-amount, purchase_id=purchase_id, inventory_id=inv_id)
    try:
        purchase_account.save_to_db()
        return jsonify({"added": "success"})
    except:
        raise SignalException("Failed to add to accounts")

@pay_supplier.connect
def make_payement(supplier_account_id: int, credit_account: int, cost: float, quantity: int):
    pass







