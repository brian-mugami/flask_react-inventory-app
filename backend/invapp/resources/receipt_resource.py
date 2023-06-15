import datetime
import io
import traceback

from sqlalchemy import desc
from xhtml2pdf import pisa
from flask import jsonify, make_response,render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
from sqlalchemy.exc import IntegrityError
from ..models.masters import CustomerModel, AccountModel
from ..models.transactions.customer_balances_model import CustomerBalanceModel
from ..models.transactions.customer_payments_model import CustomerPaymentModel
from ..models.transactions.receipt_model import ReceiptModel
from ..models.transactions.sales_accounting_models import SalesAccountingModel
from ..models.transactions.sales_models import SalesModel
from ..schemas.receiptschema import ReceiptSchema, ReceiptPaymentSchema, ReceiptVoidSchema, ReceiptPaginationSchema
from ..signals import void_receipt, SignalException, returning_balance
import pdfkit
blp = Blueprint("receipts", __name__, description="Receipt creation")

@blp.route("/receipt/download/test/<int:id>")
class ReceiptDownloadView(MethodView):
    @jwt_required(fresh=True)
    def get(self, id):
        receipt = ReceiptModel.query.get_or_404(id)
        receipt_lines = SalesModel.query.filter_by(receipt_id=receipt.id).all()
        html = render_template('receipt2.html', receipt=receipt, receipt_lines=receipt_lines)
        pdf_buffer = io.BytesIO()

        pisa.CreatePDF(html, dest=pdf_buffer)

        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={receipt.receipt_number}.pdf'

        return response


@blp.route("/receipt/download/<int:id>")
class ReceiptDownloadView(MethodView):
    @jwt_required(fresh=True)
    def get(self, id):
        receipt = ReceiptModel.query.get_or_404(id)
        receipt_lines = SalesModel.query.filter_by(receipt_id=receipt.id).all()

        response = make_response()
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={receipt.receipt_number}.pdf'

        # Create a PDF buffer
        pdf_buffer = io.BytesIO()

        # Create a PDF document
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

        # Define styles
        styles = getSampleStyleSheet()
        heading_style = styles['Heading1']
        line_item_style = ParagraphStyle(
            'LineItem',
            parent=styles['Normal'],
            spaceAfter=6,
            bulletIndent=0,
            leftIndent=20,
            bulletFontSize=8,
        )

        # Define the content
        content = []

        # Add the heading
        heading_text = f"<b>Ole Louisa Receipt: amount -{receipt.amount}</b>"
        heading = Paragraph(heading_text, heading_style)
        content.append(heading)

        # Add line items
        for item in receipt_lines:
            line_item_text = f"<bullet>&bull;</bullet>  {item.item.item_name}({item.item.item_unit}{item.item.unit_type}):{item.quantity} * {item.selling_price}-{item.item_cost}"
            line_item = Paragraph(line_item_text, line_item_style)
            content.append(line_item)

        doc.build(content)
        pdf_buffer.seek(0)

        response.set_data(pdf_buffer.getvalue())

        return response
@blp.route("/receipt/void/<int:id>")
class ReceiptVoidView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ReceiptVoidSchema)
    def post(self, data, id):
        receipt = ReceiptModel.query.get_or_404(id)
        if receipt.voided == True:
            abort(400, message="Receipt is already voided")
        if receipt.status == "not paid":
            abort(400, message="This receipt is not paid. Just delete it")
        receipt.reason = data.get("reason")
        receipt.void_receipt()
        receipt.update_db()
        try:
            void_receipt(receipt_id=receipt.id)
            return {"receipt voided": "success"}, 202
        except SignalException as e:
            traceback.print_exc()
            abort(500, message=f'{str(e)}')

@blp.route("/receipt/payment/<int:id>")
class ReceiptPaymentView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ReceiptPaymentSchema)
    @blp.response(201, ReceiptPaymentSchema)
    def post(self, data, id):
        account = AccountModel.query.filter_by(account_name=data.get("receipt_account")).first()
        if not account:
            abort(404, message="Account not found")
        receipt = ReceiptModel.query.get(id)
        customer_balance = CustomerBalanceModel.query.filter_by(receipt_id=receipt.id).order_by(CustomerBalanceModel.balance).first()
        payment = CustomerPaymentModel.query.filter_by(receipt_id=receipt.id).order_by(CustomerPaymentModel.date.desc()).first()
        if payment and payment.approval_status == "pending approval":
            abort(400, message="Please approval the last payment to create this payment")
        if payment and payment.payment_status == "fully_paid":
            abort(400, message="Payments are already fully approved")
        if not receipt:
            abort(404, message="Receipt does not exist")
        if customer_balance.balance <= 0:
            abort(400, message="This customer has no balance, either payment has been done or payment is pending approval")
        if receipt.status == "fully paid" or receipt.status == "over paid":
            abort(400, message="This receipt is already paid.")
        if receipt.accounted_status == "not_accounted":
            abort(400, "This receipt is not accounted.")
        customer_amount = CustomerBalanceModel.query.filter_by(receipt_id=id, currency=data.get("currency")).first()
        if not customer_amount:
            abort(404, message="This customer has no balance.")

        data.pop("receipt_account")
        payment = CustomerPaymentModel(
        **data,
        receipt_id=id,
        receive_account_id=account.id,
        approval_status = "pending approval",
        payment_status = "not_paid"
        )
        try:
            payment.save_to_db()
            if payment.payment_status == "fully_paid":
                pay_status = "fully paid"
            elif payment.payment_status == "partially_paid":
                pay_status = "partially paid"
            elif payment.payment_status == "not_paid":
                pay_status = "not paid"
            else:
                pay_status = "over paid"
            receipt.status = pay_status
            receipt.update_db()
            return payment
        except:
            traceback.print_exc()
            abort(500, message="Server error, Please create and review the payment again")

@blp.route("/receipt/<int:id>/account")
class ReceiptAccountingView(MethodView):
    @jwt_required(fresh=True)
    def get(self, id):
        accounting = SalesAccountingModel.query.filter_by(receipt_id=id).first()
        if not accounting:
            abort(404, message="Accounting not created for this receipt")
        debit_account = AccountModel.query.get(accounting.debit_account_id)
        credit_account = AccountModel.query.get(accounting.credit_account_id)
        credit_amount = accounting.credit_amount
        debit_amount = accounting.debit_amount

        return jsonify({"debit_account": debit_account.account_name,
                        "credit_account": credit_account.account_name,
                        "credit_amount": credit_amount,
                        "debit_amount": debit_amount})

@blp.route("/receipt")
class ReceiptView(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ReceiptPaginationSchema)
    @blp.response(200, ReceiptSchema(many=True))
    def get(self, data):
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        receipts = (ReceiptModel.query
            .order_by(desc(ReceiptModel.date))
            .paginate(page=page, per_page=per_page))
        return receipts

    @jwt_required(fresh=True)
    @blp.arguments(ReceiptSchema)
    @blp.response(201, ReceiptSchema)
    def post(self, data):
        customer = CustomerModel.query.filter_by(customer_name=data["customer_name"]).first()
        if customer is None:
            abort(404, message="Customer not found")
        data.pop("customer_name", None)
        receipt = ReceiptModel(**data)
        receipt.customer = customer
        try:
            receipt.save_to_db()
            return receipt
        except IntegrityError as e:
            abort(500, message="Ensure details are unique")

@blp.route("/receipt/<int:id>")
class ReceiptMethodView(MethodView):
    @jwt_required(fresh=True)
    def delete(self, id):
        receipt = ReceiptModel.query.get_or_404(id)
        if receipt.status != "not paid":
            abort(400, message="You cannot delete this receipt as payment has began, Please void it")
        items = SalesModel.query.filter_by(receipt_id=receipt.id).all()
        if len(items) > 0:
            for item in items:
                try:
                    returning_balance(item_id=item.item_id,item_quantity=item.quantity, receipt_id=receipt.id)
                except SignalException as e:
                    traceback.print_exc()
                    abort(400, message=f"{str(e)}")
        receipt.delete_from_db()
        return {"message":"deleted"}, 204

    @jwt_required(fresh=True)
    @blp.response(200, ReceiptSchema)
    def get(self,id):
        receipt = ReceiptModel.query.get_or_404(id)
        return receipt

    @jwt_required(fresh=True)
    @blp.arguments(ReceiptSchema)
    @blp.response(200, ReceiptSchema)
    def patch(self, data, id):
        receipt = ReceiptModel.query.get_or_404(id)
        customer = CustomerModel.query.filter_by(customer_name=data["customer_name"]).first()
        if not customer:
            abort(404, message="Customer not found")
        if receipt.status != "not paid":
            abort(400, message="You cannot edit an already paid receipt")
        if receipt.voided == True:
            abort(400, message="This receipt is already voided")
        data.pop("customer_name", None)
        receipt.description = data.get("description")
        receipt.currency = data.get("currency")
        receipt.amount = data.get("amount")
        receipt.customer = customer
        receipt.update_date = datetime.datetime.utcnow()
        receipt.update_db()
        return receipt