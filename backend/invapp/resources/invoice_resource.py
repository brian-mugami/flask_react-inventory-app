import datetime
import traceback

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from ..models.masters import SupplierModel, AccountModel
from ..models.transactions.invoice_model import InvoiceModel
from ..models.transactions.purchase_accounting_models import PurchaseAccountingModel
from ..models.transactions.supplier_balances_model import SupplierBalanceModel
from ..models.transactions.supplier_payment_models import SupplierPaymentModel
from ..schemas.invoice_schema import InvoiceSchema, InvoiceUpdateSchema, InvoicePaymentSchema, InvoiceVoidSchema, \
    InvoicePaginationSchema
from ..signals import add_supplier_balance, purchase_accounting_transaction, SignalException, void_invoice

blp = Blueprint("Invoice", __name__, description="Invoice creation")

@blp.route("/invoice/void/<int:id>")
class InvoiceVoidView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(InvoiceVoidSchema)
    @blp.response(202, InvoiceSchema)
    def post(self, data,id):
        invoice = InvoiceModel.query.get(id)
        if not invoice:
            abort(404, message="Invoice does not exist")
        if invoice.status == "not paid" and invoice.accounted == "not_accounted":
            abort(400, message= "Just delete this invoice, it has no accounting and payments")
        if invoice.status != 'not paid':
            abort(400, message='Invoice payment has began. You cannot void this invoice if payment is not voided')
        if invoice.accounting_status == "void":
            abort(400, message="This invoice is already voided")
        invoice.reason = data.get("reason")
        invoice.void_invoice()
        invoice.update_db()
        try:
            void_invoice(invoice_id=invoice.id)
            invoice.accounting_status = "void"
            invoice.update_db()
            return {"invoice voided":"success"}, 202
        except SignalException as e:
            traceback.print_exc()
            abort(500, message=f'{str(e)}')

@blp.route("/invoice/<int:id>/account")
class InvoiceAccountingView(MethodView):
    @jwt_required(fresh=True)
    def get(self, id):
        invoice = InvoiceModel.query.get(id)
        if not invoice:
            abort(404, message="Invoice does not exist")
        accounted_invoice = PurchaseAccountingModel.query.filter_by(invoice_id=invoice.id).first()
        if not accounted_invoice:
            abort(400, message="No invoice accounting on this invoice")

        debit_account = AccountModel.query.get(accounted_invoice.debit_account_id)
        credit_account = AccountModel.query.get(accounted_invoice.credit_account_id)

        return jsonify({"debit_account":debit_account.account_name, "credit_account": credit_account.account_name, "debit_amount": accounted_invoice.debit_amount, "credit_amount": accounted_invoice.credit_amount})


@blp.route("/invoice")
class Invoices(MethodView):

    @jwt_required(fresh=True)
    @blp.arguments(InvoicePaginationSchema)
    @blp.response(200,InvoiceSchema(many=True))
    def get(self, data):
        """Get all invoices"""
        #invoices = InvoiceModel.query.order_by(InvoiceModel.date.desc()).all()
        page = data.get('page', 1)
        per_page = data.get('per_page', 50)
        invoices = InvoiceModel.query.paginate(page=page, per_page=per_page)
        return invoices

    @jwt_required(fresh=True)
    @blp.arguments(InvoiceSchema)
    @blp.response(201, InvoiceSchema)
    def post(self, data):
        """Create a new invoice"""
        supplier = SupplierModel.query.filter_by(supplier_name = data["supplier_name"]).first()
        if supplier is None:
            abort(404, message="Supplier does not exist")
        invoice = InvoiceModel.query.filter_by(invoice_number=data["invoice_number"], supplier_id=supplier.id, currency=data["currency"]).first()
        if invoice:
            abort(400, message="This invoice number for this supplier already exists!!")
        if data["destination_type"] == "expense":
            account = AccountModel.query.filter_by(account_name=data["expense_account_name"], account_category="Expense Account").first()
            if not account:
                abort(404, message="Expense account not found")
            account_id = account.id
            data.pop('supplier_name', None)
            data.pop('expense_account_name', None)
            new_trx = InvoiceModel(supplier_id=supplier.id,expense_account_id=account_id,**data)
            new_trx.supplier = supplier
            new_trx.expense_account = account
            new_trx.save_to_db()
            try:
                add_supplier_balance(supplier_id=new_trx.supplier_id, invoice_id=new_trx.id,
                                     invoice_amount=new_trx.amount,
                                     currency=new_trx.currency)
                return new_trx
            except SignalException as e:
                new_trx.delete_from_db()
                abort(500, message="Did not add supplier balance")
        data.pop('supplier_name', None)
        data.pop('expense_account_name', None)
        new_trx = InvoiceModel(supplier_id=supplier.id, **data)
        new_trx.save_to_db()
        new_trx.supplier = supplier
        try:
            add_supplier_balance(supplier_id=new_trx.supplier_id, invoice_id=new_trx.id, invoice_amount=new_trx.amount,
                                 currency=new_trx.currency)
            return new_trx
        except SignalException as e:
            new_trx.delete_from_db()
            abort(500, message="Did not add supplier balance")

@blp.route("/invoice/<int:invoice_id>")
class Invoice(MethodView):

    @jwt_required(fresh=True)
    @blp.response(200,InvoiceSchema)
    def get(self, invoice_id):
        """Get an invoice by ID"""
        invoice = InvoiceModel.query.get_or_404(invoice_id)
        return invoice

    @jwt_required(fresh=True)
    @blp.arguments(InvoiceUpdateSchema)
    @blp.response(201,InvoiceSchema)
    def patch(self, invoice, invoice_id):
        """Update an existing invoice"""
        existing_invoice = InvoiceModel.query.get_or_404(invoice_id)
        if existing_invoice.accounted == "fully_accounted":
            abort(400, message="Cannot edit an accounted invoice")
        if existing_invoice.status != "not paid":
            abort(400, message="Cannot edit an invoice that has began payments")
        supplier = SupplierModel.query.filter_by(supplier_name=invoice["supplier_name"]).first()
        if supplier is None:
            abort(404, message="Supplier does not exist")
        if invoice.get("destination_type")== "expense":
            account = AccountModel.query.filter_by(account_name=invoice.get("expense_account_name"),
                                                   account_category="Expense Account").first()
            if not account:
                abort(404, message="Expense account not found")
            existing_invoice.expense_account_id = account.id
        invoice.pop("supplier_name", None)
        existing_invoice.currency = invoice["currency"]
        existing_invoice.purchase_type = invoice["purchase_type"]
        existing_invoice.destination_type = invoice["destination_type"]
        existing_invoice.invoice_number = invoice["invoice_number"]
        existing_invoice.description = invoice["description"]
        existing_invoice.amount = invoice["amount"]
        existing_invoice.update_date = datetime.datetime.utcnow()

        existing_invoice.supplier_id = supplier.id
        existing_invoice.supplier = supplier
        existing_invoice.update_date = datetime.datetime.utcnow()

        if existing_invoice.amount != existing_invoice.purchase_items[0].invoice_amount:
            existing_invoice.matched_to_lines = "unmatched"
            existing_invoice.update_db()
        else:
            existing_invoice.matched_to_lines = "matched"
            existing_invoice.update_db()
        try:
            add_supplier_balance(supplier_id=existing_invoice.supplier_id, invoice_id=existing_invoice.id, invoice_amount=existing_invoice.amount,
                                 currency=existing_invoice.currency)
            return existing_invoice
        except SignalException as e:
            abort(500, message="Did not add supplier balance")

        return existing_invoice

    @jwt_required(fresh=True)
    def delete(self, invoice_id):
        """Delete an invoice"""
        invoice = InvoiceModel.query.get_or_404(invoice_id)
        if invoice.status != "not paid":
            abort(400, message="Cannot delete an invoice with payments, instead void this invoice")
        if invoice.accounted != "not_accounted":
            abort(400, message="Cannot delete an invoice that is accounted, instead void this invoice")
        invoice.delete_from_db()
        return ({"message":"deleted"})


@blp.route("/invoice/account/<int:invoice_id>")
class InvoiceAccounting(MethodView):
    @jwt_required(fresh=True)
    @blp.response(201,InvoiceSchema)
    def post(self,invoice_id):
        invoice = InvoiceModel.query.get_or_404(invoice_id)
        if invoice.accounted == "fully_accounted" and invoice.matched_to_lines == "matched":
            abort(400, message="Invoice is already accounted and matched")
        if invoice.matched_to_lines == "unmatched":
            abort(400, message="Invoice is unmatched. Add invoice lines to allow accounting")
        invoice.accounted = "fully_accounted"
        invoice.matched_to_lines = "matched"
        invoice.update_db()
        if invoice.destination_type == "expense":
            try:
                supplier_account = invoice.supplier.account_id
                try:
                    purchase_accounting_transaction(invoice_id=invoice.id, purchase_account_id=invoice.expense_account_id,
                                               supplier_account_id=supplier_account, invoice_amount=invoice.amount,)
                    return invoice
                except SignalException as e:
                    abort(500, message=f"Failed to add expense please try again: {str(e)}")
            except:
                traceback.print_exc()
                abort(500, message="Did not save to the db")

        if invoice.purchase_type == "cash" and invoice.destination_type == "stores":
            """cash purchase"""
            try:
                purchase_account = AccountModel.query.filter_by(account_type="cash", account_category="Purchase Account").first()
                supplier_account = invoice.supplier.account_id
                try:
                    purchase_accounting_transaction(invoice_id=invoice.id, purchase_account_id=purchase_account.id,
                                                   supplier_account_id=supplier_account,
                                                   invoice_amount=invoice.amount, )
                    return invoice
                except SignalException as e:
                    abort(500, message=f"Failed to add to store, please try again: {str(e)}")

            except:
                traceback.print_exc()
                abort(500, message="Did not save to the db")

        if invoice.purchase_type == "credit" and invoice.destination_type == "stores":
            try:
                purchase_account = AccountModel.query.filter_by(account_type="credit", account_category="Purchase Account").first()
                supplier_account = invoice.supplier.account_id
                try:
                    purchase_accounting_transaction(invoice_id=invoice.id, purchase_account_id=purchase_account.id,
                                                   supplier_account_id=supplier_account,
                                                   invoice_amount=invoice.amount, )
                    return invoice
                except:
                    abort(500, message="Failed to add to store, please try again")
            except:
                traceback.print_exc()
                abort(500, message=f"Did not save to the db")

@blp.route("/invoice/payment/<int:invoice_id>")
class PaymentView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(InvoicePaymentSchema)
    @blp.response(201, InvoicePaymentSchema)
    def post(self, data, invoice_id):
        bank_account = AccountModel.query.filter_by(account_name=data["bank_account"], account_category="Bank Account").first()
        payment = SupplierPaymentModel.query.filter_by(invoice_id=invoice_id).order_by(SupplierPaymentModel.date.desc()).first()
        if payment and payment.approval_status == "pending approval":
            abort(400, message="Please approve the recent payments so as to create this payment")
        if not bank_account:
            abort(404, message="Bank account not found")
        invoice = InvoiceModel.query.get(invoice_id)
        if not invoice:
            abort(404, message="Could not find invoice")
        if invoice.accounted != "fully_accounted":
            abort(400, message="This invoice is not accounted")
        if invoice.status == "fully paid":
            abort(400, message="Invoice is already fully paid")
        purchase_amount = SupplierBalanceModel.query.filter_by(invoice_id=invoice.id, currency=data["currency"]).first()
        if purchase_amount.balance == 0:
            abort(400, message="This supplier balance is fully sorted, Please check your payments and approve them")
        if purchase_amount.balance < data["amount"]:
            abort(400, message="Amount is higher than the balance")

        data.pop("bank_account")
        payment = SupplierPaymentModel(
        **data,
        bank_account_id = bank_account.id,
        invoice_id = invoice.id,
        approval_status = 'pending approval',
        payment_status = 'not paid'
        )
        payment.invoice = invoice
        payment.account = bank_account
        payment.save_to_db()
        invoice.status = payment.payment_status
        invoice.update_db()
        return payment


