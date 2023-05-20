import datetime

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from flask_jwt_extended import jwt_required
from ..db import db
from ..models.transactions.invoice_model import InvoiceModel
from ..models.transactions.receipt_model import ReceiptModel

blp = Blueprint("Transactions", __name__, description="Actions on dashboard accounts")

#https://kindredinv.onrender.com/transaction/sales
@blp.route("/transaction/sales")
class SalesTransaction(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        current_date = datetime.datetime.now().date()
        query = db.session.query(
            db.func.count().label('total_transactions'),
            db.func.sum(ReceiptModel.amount).label('total_sales_amount')
        ).filter(
            db.or_(
                ReceiptModel.status == 'fully paid',
                ReceiptModel.status == 'partially paid'
            ),
            db.func.date(ReceiptModel.date) == current_date
        ).first()

        total_transactions = query.total_transactions
        total_sales_amount = query.total_sales_amount
        return jsonify({"Sales": total_transactions, "Amount": total_sales_amount}), 200

@blp.route("/transaction/purchase")
class PurchaseTransaction(MethodView):

    def get(self):
        current_date = datetime.datetime.now().date()
        query = db.session.query(
            db.func.count().label('total_transactions'),
            db.func.sum(InvoiceModel.amount).label('total_purchase_amount')
        ).filter(
            db.or_(
                InvoiceModel.matched_to_lines == 'matched',
                InvoiceModel.matched_to_lines == 'partially matched'
            ),
            db.func.date(InvoiceModel.date) == current_date
        ).first()

        total_transactions = query.total_transactions
        total_purchase_amount = query.total_purchase_amount
        return jsonify({"Purchases": total_transactions, "Amount": total_purchase_amount}), 200

