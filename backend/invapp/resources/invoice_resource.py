from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..models import SupplierModel
from ..models.transactions.invoice_model import InvoiceModel
from ..schemas.invoice_schema import InvoiceSchema

invoices_bp = Blueprint("invoices", "invoices", url_prefix="/invoices")

@invoices_bp.route("/")
class Invoices(MethodView):

    @invoices_bp.response(200,InvoiceSchema(many=True))
    def get(self):
        """Get all invoices"""
        invoices = InvoiceModel.query.all()
        return invoices

    @invoices_bp.arguments(InvoiceSchema)
    @invoices_bp.response(201, InvoiceSchema)
    def post(self, invoice):
        """Create a new invoice"""
        supplier = SupplierModel.query.get(invoice["supplier_id"])
        if supplier is None:
            abort(400, message="Invalid supplier ID")
        new_invoice = InvoiceModel(**invoice)
        new_invoice.supplier = supplier
        new_invoice.save_to_db()
        return new_invoice, 201

@invoices_bp.route("/<int:invoice_id>")
class Invoice(MethodView):

    @invoices_bp.response(200,InvoiceSchema)
    def get(self, invoice_id):
        """Get an invoice by ID"""
        invoice = InvoiceModel.query.get_or_404(invoice_id)
        return invoice

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
        return existing_invoice

    def delete(self, invoice_id):
        """Delete an invoice"""
        invoice = InvoiceModel.query.get_or_404(invoice_id)
        invoice.delete_from_db()
        return ({"message":"deleted"})
