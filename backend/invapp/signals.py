import datetime

from blinker import signal

from invapp.models.transactions.inventory_balances import InventoryBalancesModel
from invapp.models.transactions.purchase_accounting_models import PurchaseAccountingModel, SupplierPayAccountingModel
from invapp.models.transactions.supplier_balances_model import SupplierBalanceModel
from flask import jsonify
from invapp.models.transactions.sales_accounting_models import SalesAccountingModel

send_data = signal('send-data')
purchase_account = signal('purchase_account')
pay_supplier = signal("pay-supplier")
supplier_balance = signal("supplier_balance")
sales_account = signal("sales_account")

class SignalException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

@send_data.connect
def increase_stock_addition(item_id: int,purchase_id:int, cost: float, quantity: int, date: str=None, supplier_id: int=None):
    item = InventoryBalancesModel.query.filter_by(purchase_id=purchase_id, item_id=item_id).first()
    if item:
        item.cost = cost
        item.quantity = quantity
        item.update_date = datetime.datetime.utcnow()
        item.update_db()
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
        existing_accounting.credit_account_id = supplier_account_id
        existing_accounting.debit_account_id = purchase_account_id
        existing_accounting.credit_amount = -amount
        existing_accounting.debit_amount = amount
        existing_accounting.update_date = datetime.datetime.utcnow()
        existing_accounting.update_db()
        return jsonify({"message": "updated"})
    purchase_account = PurchaseAccountingModel(credit_account_id=supplier_account_id,debit_account_id=purchase_account_id,
                                          debit_amount=amount, credit_amount=-amount, purchase_id=purchase_id, inventory_id=inv_id)
    try:
        purchase_account.save_to_db()
        return jsonify({"added": "success"})
    except:
        raise SignalException("Failed to add to accounts")

@pay_supplier.connect
def make_payement(supplier_account_id: int, credit_account: int, amount: float, payment_id: int, balance_id: int):
    existing = SupplierPayAccountingModel.query.filter_by(payment_id=payment_id, balance_id=balance_id).first()
    if existing:
        existing.update_date = datetime.datetime.utcnow()
        existing.credit_amount = -amount
        existing.debit_amount = amount
        existing.credit_account_id = credit_account
        existing.debit_account_id = supplier_account_id
        existing.update_db()
        return jsonify({"message": "updated"})
    else:
        new_payment = SupplierPayAccountingModel(credit_amount = -amount, debit_amount= amount, credit_account_id= credit_account, debit_account_id=supplier_account_id, payment_id=payment_id, balance_id=balance_id)
        try:
            new_payment.save_to_db()
        except:
            raise SignalException("Payment failed")


@supplier_balance.connect
def add_supplier_balance(supplier_id: int,purchase_id: int,invoice_amount: float , currency: str = "KES", paid: float = 0.00):
    balance = invoice_amount - paid

    existing_balance = SupplierBalanceModel.query.filter_by(supplier_id=supplier_id, currency=currency, purchase_id=purchase_id).first()
    if existing_balance:
        existing_balance.paid += paid
        existing_balance.invoice_amount = invoice_amount
        existing_balance.balance -= paid
        existing_balance.date = datetime.datetime.utcnow()
        existing_balance.update_db()
        return existing_balance.id
    else:
        sup_balance = SupplierBalanceModel(supplier_id=supplier_id, purchase_id=purchase_id, invoice_amount=invoice_amount, paid=paid, balance=balance, currency=currency, date=datetime.datetime.utcnow())
        try:
            sup_balance.save_to_db()
            return sup_balance.id
        except:
            raise SignalException("supplier balance update failed")


@sales_account.connect
def sales_accounting_transaction(sales_account_id: int, sale_id: int,customer_account_id: int, cost: float, quantity: int, inv_id: int):
    amount = cost * quantity
    existing_accounting = SalesAccountingModel.query.filter_by(sale_id=sale_id).first()
    if existing_accounting:
        existing_accounting.credit_account_id = customer_account_id
        existing_accounting.debit_account_id = sales_account_id
        existing_accounting.credit_amount = -amount
        existing_accounting.debit_amount = amount
        existing_accounting.update_date = datetime.datetime.utcnow()
        existing_accounting.update_db()
        return jsonify({"message": "updated"})
    sales_account = SalesAccountingModel(credit_account_id=customer_account_id,debit_account_id=sales_account_id,
                                          debit_amount=amount, credit_amount=-amount, sale_id=sale_id)
    try:
        sales_account.save_to_db()
        return jsonify({"added": "success"})
    except:
        raise SignalException("Failed to add to accounts")




