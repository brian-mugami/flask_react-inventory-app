import traceback

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from ..models import SupplierModel, AccountModel
from ..models.transactions.invoice_model import InvoiceModel
from ..schemas.invoice_schema import InvoiceSchema, InvoiceApproveSchema
from ..signals import add_supplier_balance, purchase_accouting_transaction, SignalException

invoices_bp = Blueprint("invoices", "invoices", url_prefix="/invoices")

@invoices_bp.route("/")
class Invoices(MethodView):
    @jwt_required(fresh=True)
    @invoices_bp.response(200,InvoiceSchema(many=True))
    def get(self):
        """Get all invoices"""
        invoices = InvoiceModel.query.all()
        return invoices

    @jwt_required(fresh=True)
    @invoices_bp.arguments(InvoiceSchema)
    @invoices_bp.response(201, InvoiceSchema)
    def post(self, data):
        """Create a new invoice"""
        supplier = SupplierModel.query.get(data["supplier_id"])
        if supplier is None:
            abort(400, message="Invalid supplier ID")
        invoice = InvoiceModel.query.filter_by(invoice_number=data["invoice_number"], supplier_id=data["supplier_id"]).first()
        if invoice:
            abort(400, message="This invoice number for this supplier already exists!!")
        new_trx = InvoiceModel(**data)
        new_trx.supplier = supplier
        new_trx.save_to_db()
        try:
            add_supplier_balance(supplier_id=new_trx.supplier_id, invoice_id=new_trx.id, invoice_amount=new_trx.amount,
                                 currency=new_trx.currency)
            return new_trx
        except SignalException as e:
            new_trx.delete_from_db()
            abort(500, message="Did not ass supplier balance")

@invoices_bp.route("/<int:invoice_id>")
class Invoice(MethodView):

    @jwt_required(fresh=True)
    @invoices_bp.response(200,InvoiceSchema)
    def get(self, invoice_id):
        """Get an invoice by ID"""
        invoice = InvoiceModel.query.get_or_404(invoice_id)
        return invoice

    @jwt_required(fresh=True)
    @invoices_bp.arguments(InvoiceSchema)
    @invoices_bp.response(201,InvoiceSchema)
    def patch(self, invoice, invoice_id):
        """Update an existing invoice"""
        existing_invoice = InvoiceModel.query.get_or_404(invoice_id)
        supplier = SupplierModel.query.get(invoice["supplier_id"])
        if supplier is None:
            abort(400, message="Invalid supplier ID")
        existing_invoice.update_from_dict(invoice)
        existing_invoice.supplier = supplier
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
        invoice.delete_from_db()
        return ({"message":"deleted"})


@invoices_bp.route("/account/<int:invoice_id>")
class InvoiceAccounting(MethodView):
    @jwt_required(fresh=True)
    @invoices_bp.arguments(InvoiceApproveSchema)
    @invoices_bp.response(201,InvoiceSchema)
    def post(self, data,invoice_id):
        invoice = InvoiceModel.query.get_or_404(invoice_id)
        if invoice.accounted and invoice.matched_to_lines == "matched":
            abort(400, message="Invoice is already accounted and matched")
        if invoice.matched_to_lines == "unmatched":
            abort(400, message="Invoice is unmatched. Add invoice lines to allow accounting")
        invoice.accounted = True
        invoice.update_db()
        if invoice.purchase_type == "cash" and invoice.destination_type == "expense":
            try:
                expense_account = AccountModel.query.filter_by(account_name=data["expense_type"],account_type="cash",
                                                                account_category="Expense Account").first()
                supplier_account = invoice.supplier.account_id
                try:
                    purchase_accouting_transaction(invoice_id=invoice.id, purchase_account_id=expense_account.id,
                                               supplier_account_id=supplier_account, invoice_amount=invoice.amount,)
                    return invoice
                except SignalException as e:
                    abort(500, message=f"Failed to add expense please try again: {str(e)}")
            except:
                traceback.print_exc()
                abort(500, message="Did not save to the db")

        if invoice.purchase_type == "credit" and invoice.destination_type == "expense":
            try:
                expense_account = AccountModel.query.filter_by(account_type="credit",account_name=data["expense_type"],
                                                                account_category="Expense Account", ).first()
                supplier_account = invoice.supplier.account_id
                try:
                    purchase_accouting_transaction(invoice_id=invoice.id, purchase_account_id=expense_account.id,
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
                    purchase_accouting_transaction(invoice_id=invoice.id, purchase_account_id=purchase_account.id,
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
                    purchase_accouting_transaction(invoice_id=invoice.id, purchase_account_id=purchase_account.id,
                                                   supplier_account_id=supplier_account,
                                                   invoice_amount=invoice.amount, )
                    return invoice
                except:
                    abort(500, message="Failed to add to store, please try again")
            except:
                traceback.print_exc()
                abort(500, message=f"Did not save to the db")



