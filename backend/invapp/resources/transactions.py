import datetime

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..db import db
from ..models.transactions.invoice_model import InvoiceModel
from ..models.transactions.receipt_model import ReceiptModel

blp = Blueprint("Transactions", __name__, description="Actions on dashboard accounts")


# https://kindredinv.onrender.com/transaction/sales
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
    @jwt_required(fresh=True)
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

@blp.route("/transaction/sales/per_day")
class SalesGraphView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        today = datetime.datetime.now().date()
        start_of_week = today - datetime.timedelta(days=today.weekday())  # Get the start of the current week
        end_of_week = start_of_week + datetime.timedelta(days=6)  # Get the end of the current week

        sales_by_weekday = (
            db.session.query(
                func.to_char(ReceiptModel.date, 'Day').label('weekday'),
                func.sum(ReceiptModel.amount)
            )
            .filter(ReceiptModel.date.between(start_of_week, end_of_week))
            .group_by('weekday')
            .all()
        )

        sales_data = {
            weekday: float(total_amount)
            for weekday, total_amount in sales_by_weekday
        }

        return sales_data


@blp.route("/transaction/purchases/per_day")
class PurchaseGraphView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        today = datetime.datetime.now().date()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        purchase_by_weekday = (
            db.session.query(
                func.to_char(InvoiceModel.date, 'Day').label('weekday'),
                func.sum(InvoiceModel.amount),
                InvoiceModel.matched_to_lines == "matched"
            )
            .filter(InvoiceModel.date.between(start_of_week, end_of_week))
            .group_by('weekday')
            .all()
        )

        purchase_data = {
            weekday: float(total_amount)
            for weekday, total_amount in purchase_by_weekday
        }

        return purchase_data

@blp.route("/transaction/expenses/per_day")
class ExpenseDailyView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        today = datetime.datetime.now().date()
        start_of_week = today - datetime.timedelta(days=today.weekday())  # Get the start of the current week
        end_of_week = start_of_week + datetime.timedelta(days=6)  # Get the end of the current week

        purchase_by_weekday = (
            db.session.query(
                func.to_char(InvoiceModel.date, 'Day').label('weekday'),
                func.sum(InvoiceModel.amount)
            )
            .filter(InvoiceModel.date.between(start_of_week, end_of_week),
                    InvoiceModel.destination_type=="expense",
                    InvoiceModel.matched_to_lines == "matched")
            .group_by('weekday')
            .all()
        )

        purchase_data = {
            weekday: float(total_amount)
            for weekday, total_amount in purchase_by_weekday
        }

        return purchase_data

