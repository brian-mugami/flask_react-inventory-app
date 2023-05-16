import datetime
import traceback

from blinker import signal

from .models.masters import AccountModel
from .models.transactions.bank_balances_model import BankBalanceModel
from .models.transactions.inventory_balances import InventoryBalancesModel
from .models.transactions.invoice_model import InvoiceModel
from .models.transactions.purchase_accounting_models import PurchaseAccountingModel, SupplierPayAccountingModel
from .models.transactions.receipt_model import ReceiptModel
from .models.transactions.supplier_balances_model import SupplierBalanceModel
from .models.transactions.customer_balances_model import CustomerBalanceModel
from .models.transactions.expenses_model import ExpensesModel
from flask import jsonify
from .models.transactions.sales_accounting_models import SalesAccountingModel, CustomerPayAccountingModel

void_receipt = signal("void_receipt")
reverse_accounting = signal('reverse-accounting')
send_data = signal('send-data')
purchase_account = signal('purchase_account')
pay_supplier = signal("pay-supplier")
supplier_balance = signal("supplier_balance")
sales_account = signal("sales_account")
customer_balance = signal("customer_balance")
customer_payment = signal("customer_payment")
expense_addition = signal("signal_addition")
bank_balance = signal("bank_balance")

class SignalException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

@void_receipt.connect
def void_receipt(receipt_id:int):
    accounting_receipt = SalesAccountingModel.query.filter_by(receipt_id=receipt_id).first()
    if not accounting_receipt:
        raise SignalException("This receipt has no accounting")
    if accounting_receipt.receipt.voided:
        raise SignalException("This receipt is already voided")
    voided = SalesAccountingModel(receipt_id=receipt_id, debit_account_id=accounting_receipt.credit_account_id, credit_account_id=accounting_receipt.debit_account_id,accounting_status="void", credit_amount=accounting_receipt.credit_amount, debit_amount=accounting_receipt.debit_amount)
    try:
        voided.save_to_db()
    except:
        traceback.print_exc()
        raise SignalException("Failed to void!! Please try again")

@reverse_accounting.connect
def void_invoice(invoice_id: int):
    accounting_invoice = PurchaseAccountingModel.query.filter_by(invoice_id=invoice_id).first()
    if not accounting_invoice:
        raise SignalException("This invoice has no accounting")
    if accounting_invoice.accounting_status == "void":
        raise SignalException("You have already voided this invoice!!")
    voided = PurchaseAccountingModel(invoice_id=invoice_id, debit_account_id=accounting_invoice.credit_account_id, credit_account_id=accounting_invoice.debit_account_id, accounting_status="void", credit_amount=accounting_invoice.credit_amount, debit_amount=accounting_invoice.debit_amount)
    try:
        voided.save_to_db()
    except:
        traceback.print_exc()
        raise SignalException("Failed to void!! Please try again")


@bank_balance.connect
def manipulate_bank_balance(bank_account_id: int, invoice_id: int = None, receipt_id: int = None, amount: float = 0.00, currency: str ="KES", date = None):
    bank = AccountModel.query.get(bank_account_id)
    if bank is None or bank_account_id is None:
        raise SignalException("You have not set a bank account")
    existing_balance = BankBalanceModel.query.filter_by(invoice_id=invoice_id, receipt_id=receipt_id, bank_account_id=bank_account_id).first()
    if existing_balance:
        existing_balance.invoice_amount = amount
        existing_balance.update_date = datetime.datetime.utcnow()
        existing_balance.currency = currency
        existing_balance.update_db()
    balance = BankBalanceModel(invoice_id=invoice_id, receipt_id=receipt_id, bank_account_id=bank_account_id, currency=currency,amount=amount)
    try:
        balance.save_to_db()
    except :
        raise SignalException("Failed to add to bank balance")

@expense_addition.connect
def expense_addition(item_id,invoice_id:int, quantity: int, unit_cost: int,date: str=None):
    item = ExpensesModel.query.filter_by(invoice_id=invoice_id, item_id=item_id).first()
    if item:
        item.unit_cost = unit_cost
        item.quantity = quantity
        item.update_date = datetime.datetime.utcnow()
        item.update_db()
        return item.id
    onhand_item = ExpensesModel(item_id=item_id, invoice_id=invoice_id,unit_cost=unit_cost, quantity=quantity, date=date)
    try:
        onhand_item.save_to_db()
        return onhand_item.id
    except:
        raise SignalException("Failed to add to expense")

@send_data.connect
def increase_stock_addition(item_id,invoice_id:int,quantity: int, unit_cost: int, date: str=None):
    item = InventoryBalancesModel.query.filter_by(invoice_id=invoice_id, item_id=item_id).first()
    if item:
        item.unit_cost = unit_cost
        item.quantity = quantity
        item.update_date = datetime.datetime.utcnow()
        item.update_db()
        return item.id
    onhand_item = InventoryBalancesModel(item_id=item_id, invoice_id=invoice_id,unit_cost=unit_cost, quantity=quantity, date=date)
    try:
        onhand_item.save_to_db()
        return onhand_item.id
    except:
        raise SignalException("Failed to add to stores")


@purchase_account.connect
def purchase_accounting_transaction(purchase_account_id: int, invoice_id: int,supplier_account_id: int,invoice_amount: float):
    if purchase_account_id is None or supplier_account_id is None:
        raise SignalException("You have to set up a purchase account or supplier account")
    existing_accounting = PurchaseAccountingModel.query.filter_by(invoice_id=invoice_id).first()
    if existing_accounting:
        existing_accounting.credit_account_id = supplier_account_id
        existing_accounting.debit_account_id = purchase_account_id
        existing_accounting.debit_amount = invoice_amount
        existing_accounting.credit_amount = -invoice_amount
        existing_accounting.update_db()
    purchase_account = PurchaseAccountingModel(credit_account_id=supplier_account_id,debit_account_id=purchase_account_id,
                                          debit_amount=invoice_amount, credit_amount=-invoice_amount, invoice_id=invoice_id, accounting_status='account')
    try:
        purchase_account.save_to_db()
        return jsonify({"added": "success"})
    except:
        raise SignalException("Failed to add to accounts")

@pay_supplier.connect
def make_payement(supplier_account_id: int, credit_account: int, amount: float, payment_id: int, balance_id: int):
    if supplier_account_id is None or credit_account is None:
        raise SignalException("Create supplier account first and a credit account")
    balance = SupplierBalanceModel.query.get(balance_id)
    if balance.balance < 0:
        raise SignalException("This balance is already fully sorted")
    new_payment = SupplierPayAccountingModel(credit_amount = -amount, debit_amount= amount, credit_account_id= credit_account, debit_account_id=supplier_account_id, payment_id=payment_id, balance_id=balance_id)
    try:
        new_payment.save_to_db()
    except:
        raise SignalException("Payment failed")

@customer_payment.connect
def receive_payment(customer_account_id: int, bank_account: int, amount: float, payment_id: int, balance_id: int):
    if customer_account_id is None or bank_account is None:
        raise SignalException("Create a customer account and bank account first.")
    balance = CustomerBalanceModel.query.get(balance_id)
    if balance.balance < 0:
        raise SignalException("This balance is already fully sorted")
    new_payment = CustomerPayAccountingModel(credit_amount = -amount, debit_amount= amount, credit_account_id= customer_account_id, debit_account_id=bank_account, payment_id=payment_id, balance_id=balance_id)
    try:
        new_payment.save_to_db()
    except:
        raise SignalException("Payment failed")


@supplier_balance.connect
def add_supplier_balance(supplier_id: int,invoice_id: int,invoice_amount: float , currency: str = "KES",payment_id: int = None, paid: float = 0.00):
    balance = invoice_amount - paid
    invoice = InvoiceModel.query.get_or_404(invoice_id)
    existing_balance = SupplierBalanceModel.query.filter_by(supplier_id=supplier_id, currency=currency, invoice_id=invoice_id).first()
    if existing_balance:
        existing_balance.balance = invoice_amount
        existing_balance.paid += paid
        existing_balance.invoice_amount = invoice_amount
        existing_balance.balance -= paid
        existing_balance.date = datetime.datetime.utcnow()
        existing_balance.update_db()
        return existing_balance.id
    else:
        sup_balance = SupplierBalanceModel(supplier_id=supplier_id, invoice_id=invoice_id, invoice_amount=invoice_amount, paid=paid, balance=balance, currency=currency, date=datetime.datetime.utcnow(), payment_id=payment_id)
        try:
            sup_balance.save_to_db()
            sup_balance.invoice = invoice
            return sup_balance.id
        except:
            traceback.print_exc()
            invoice.delete_from_db()
            raise SignalException("supplier balance update failed")

@sales_account.connect
def sales_accounting_transaction(sales_account_id: int, receipt_id: int,customer_account_id: int,amount:float):
    if sales_account_id is None or customer_account_id is None:
        raise SignalException("Please create a sales account and a customer account")
    existing_sale_accounting = SalesAccountingModel.query.filter_by(receipt_id=receipt_id).first()
    if existing_sale_accounting:
        existing_sale_accounting.credit_account_id = sales_account_id
        existing_sale_accounting.debit_account_id = customer_account_id
        existing_sale_accounting.debit_amount = amount
        existing_sale_accounting.credit_amount = -amount
        existing_sale_accounting.update_date = datetime.datetime.utcnow()
        existing_sale_accounting.update_db()
    sales_account = SalesAccountingModel(credit_account_id=sales_account_id,debit_account_id=customer_account_id,
                                          debit_amount=amount, credit_amount=-amount, receipt_id=receipt_id)
    try:
        sales_account.save_to_db()
        return jsonify({"added": "success"})
    except:
        raise SignalException("Failed to add to accounts")


@customer_balance.connect
def add_customer_balance(customer_id: int,receipt_id: int,receipt_amount: float , currency: str = "KES", paid: float = 0.00):
    balance = receipt_amount - paid
    receipt = ReceiptModel.query.get_or_404(receipt_id)
    existing_balance = CustomerBalanceModel.query.filter_by(customer_id=customer_id, currency=currency,
                                                            receipt_id=receipt_id).first()
    if existing_balance:
        existing_balance.paid += paid
        existing_balance.receipt_amount = receipt_amount
        existing_balance.balance -= paid
        existing_balance.date = datetime.datetime.utcnow()
        existing_balance.balance = receipt_amount
        existing_balance.update_db()
        return existing_balance.id
    else:
        sup_balance = CustomerBalanceModel(customer_id=customer_id, receipt_id=receipt_id,
                                           receipt_amount=receipt_amount, paid=paid, balance=balance, currency=currency,
                                           date=datetime.datetime.utcnow())
        try:
            sup_balance.save_to_db()
            sup_balance.receipt = receipt
            return sup_balance.id
        except:
            receipt.delete_from_db()
            raise SignalException("customer balance update failed")



