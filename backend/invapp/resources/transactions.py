import datetime

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import func, text

from ..db import db
from ..models.transactions.inventory_balances import InventoryBalancesModel
from ..models.transactions.invoice_model import InvoiceModel
from ..models.transactions.receipt_model import ReceiptModel

blp = Blueprint("Transactions", __name__, description="Actions on dashboard accounts")


# https://kindredinv.onrender.com/transaction/sales
@blp.route("/transaction/purchase/month")
class PurchaseTransactionsMonthly(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        # Get the current month and year
        today = datetime.datetime.now()
        current_month = today.month
        current_year = today.year

        # Calculate the first and last day of the current month
        first_day = datetime.datetime(current_year, current_month, 1)
        last_day = datetime.datetime(current_year, current_month + 1, 1) - datetime.timedelta(days=1)

        # Generate a list of all dates within the current month
        date_range = [first_day + datetime.timedelta(days=x) for x in range((last_day - first_day).days + 1)]

        # Query the database to get the total amount per day for the current month
        daily_totals = db.session.query(func.date(InvoiceModel.date).label('day'),
                                        func.coalesce(func.sum(InvoiceModel.amount), 0).label('total_amount')).filter(
            InvoiceModel.matched_to_lines == "matched",
            func.extract('year', InvoiceModel.date) == current_year,
            func.extract('month', InvoiceModel.date) == current_month
        ).group_by(func.date(InvoiceModel.date)).order_by(func.date(InvoiceModel.date)).all()

        # Create a dictionary for each day with the date, name of the day, and total amount
        daily_totals_data = []
        for date in date_range:
            day_str = date.strftime('%Y-%m-%d')
            day_name = date.strftime('%A')
            total_amount = next((row.total_amount for row in daily_totals if row.day.strftime('%Y-%m-%d') == day_str),
                                0)
            daily_totals_data.append({'day': day_str, 'day_name': day_name, 'total_amount': total_amount})

        return {'daily_totals': daily_totals_data}, 200


@blp.route("/transaction/sales/month")
class SalesTransactionsMonthly(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        # Get the current month and year
        today = datetime.datetime.now()
        current_month = today.month
        current_year = today.year

        # Calculate the first and last day of the current month
        first_day = datetime.datetime(current_year, current_month, 1)
        last_day = datetime.datetime(current_year, current_month + 1, 1) - datetime.timedelta(days=1)

        # Generate a list of all dates within the current month
        date_range = [first_day + datetime.timedelta(days=x) for x in range((last_day - first_day).days + 1)]

        # Query the database to get the total amount per day for the current month
        daily_totals = db.session.query(func.date(ReceiptModel.date).label('day'),
                                        func.coalesce(func.sum(ReceiptModel.amount), 0).label('total_amount')).filter(
            func.extract('year', ReceiptModel.date) == current_year,
            func.extract('month', ReceiptModel.date) == current_month
        ).group_by(func.date(ReceiptModel.date)).order_by(func.date(ReceiptModel.date)).all()

        # Create a dictionary for each day with the date, name of the day, and total amount
        daily_totals_data = []
        for date in date_range:
            day_str = date.strftime('%Y-%m-%d')
            day_name = date.strftime('%A')
            total_amount = next((row.total_amount for row in daily_totals if row.day.strftime('%Y-%m-%d') == day_str),
                                0)
            daily_totals_data.append({'day': day_str, 'day_name': day_name, 'total_amount': total_amount})

        return {'daily_totals': daily_totals_data}, 200


@blp.route("/transaction/sales")
class SalesTransaction(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        current_date = datetime.datetime.now().date()
        yesterday = current_date - datetime.timedelta(days=1)
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

        yesterday_transactions = db.session.query(
            db.func.count().label('total_transactions'),
            db.func.sum(ReceiptModel.amount).label('total_sales_amount')
        ).filter(
            db.or_(
                ReceiptModel.status == 'fully paid',
                ReceiptModel.status == 'partially paid'
            ),
            db.func.date(ReceiptModel.date) == yesterday
        ).first()

        last_transactions = yesterday_transactions.total_transactions
        last_sales = yesterday_transactions.total_sales_amount

        total_transactions = query.total_transactions
        total_sales_amount = query.total_sales_amount

        if last_sales is not None and total_sales_amount is not None:
            if last_sales != 0:
                percentage = (total_sales_amount - last_sales) / last_sales * 100
            else:
                percentage = 0
        else:
            percentage = 0

        return jsonify({"Sales": total_transactions, "Yesterday_Sales": last_sales, "Amount": total_sales_amount,
                        "Percentage_sales": percentage}), 200


@blp.route("/transaction/purchase")
class PurchaseTransaction(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        current_date = datetime.datetime.now().date()
        yesterday = current_date - datetime.timedelta(days=1)
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

        query_yesterday = db.session.query(
            db.func.count().label('total_transactions'),
            db.func.sum(InvoiceModel.amount).label('total_purchase_amount')
        ).filter(
            db.or_(
                InvoiceModel.matched_to_lines == 'matched',
                InvoiceModel.matched_to_lines == 'partially matched'
            ),
            db.func.date(InvoiceModel.date) == yesterday
        ).first()

        query_yesterday_transactions = query_yesterday.total_transactions
        query_yesterday_purchases = query_yesterday.total_purchase_amount

        total_transactions = query.total_transactions
        total_purchase_amount = query.total_purchase_amount

        if query_yesterday_purchases is not None and total_purchase_amount is not None:
            if query_yesterday_purchases != 0:
                percentage = (total_purchase_amount - query_yesterday_purchases) / query_yesterday_purchases * 100
            else:
                percentage = 0
        else:
            percentage = 0

        return jsonify({"Purchases": total_transactions, "Yesterday_purchase": query_yesterday_transactions,
                        "Amount": total_purchase_amount, "Percentage_Purchase": percentage}), 200


@blp.route("/transaction/sales/per_day")
class SalesGraphView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        today = datetime.datetime.now().date()
        start_of_week = today - datetime.timedelta(days=today.weekday())  # Get the start of the current week
        end_of_week = start_of_week + datetime.timedelta(days=6)  # Get the end of the current week

        sales_by_weekday = (
            db.session.query(
                func.trim(func.to_char(ReceiptModel.date, 'Day')).label('weekday'),
                func.sum(ReceiptModel.amount)
            )
            .filter(
                ReceiptModel.date.between(start_of_week, end_of_week),
            )
            .group_by('weekday')
            .all()
        )

        sales_data = {
            weekday: float(total_amount)
            for weekday, total_amount in sales_by_weekday
        }
        total_sales_week = sum(float(total_amount) for _, total_amount in sales_by_weekday)
        sales_data['total_sales_week'] = total_sales_week

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
                func.trim(func.to_char(InvoiceModel.date, 'Day')).label('weekday'),
                func.sum(InvoiceModel.amount),
            )
            .filter(InvoiceModel.date.between(start_of_week, end_of_week))
            .group_by('weekday')
            .all()
        )

        purchase_data = {
            weekday: float(total_amount)
            for weekday, total_amount in purchase_by_weekday
        }

        total_sales_week = sum(float(total_amount) for _, total_amount in purchase_by_weekday)
        purchase_data['total_purchases_week'] = total_sales_week
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
                func.trim(func.to_char(InvoiceModel.date, 'Day')).label('weekday'),
                func.sum(InvoiceModel.amount)
            )
            .filter(InvoiceModel.date.between(start_of_week, end_of_week),
                    InvoiceModel.destination_type == "expense")
            .group_by('weekday')
            .all()
        )

        purchase_data = {
            weekday: float(total_amount)
            for weekday, total_amount in purchase_by_weekday
        }
        total_sales_week = sum(float(total_amount) for _, total_amount in purchase_by_weekday)
        purchase_data['total_expenses_week'] = total_sales_week

        return purchase_data


@blp.route("/transaction/inventory-count")
class InventoryDailyView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        total_value = db.session.query(
            db.func.sum(InventoryBalancesModel.unit_cost * InventoryBalancesModel.quantity)).scalar()
        return {"total_value": total_value}


@blp.route("/transaction/purchase/credit")
class PurchaseCreditViews(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        query = text('''
            SELECT suppliers.supplier_name, SUM(supplier_balances.balance) AS total_balance
            FROM invoices
            JOIN suppliers ON invoices.supplier_id = suppliers.id
            JOIN supplier_balances ON invoices.supplier_id = supplier_balances.supplier_id
            WHERE invoices.accounted = 'fully_accounted'
                AND invoices.status != 'fully paid'
                AND invoices.purchase_type = 'credit'
            GROUP BY suppliers.supplier_name, invoices.date
            ORDER BY total_balance ASC, invoices.date ASC
            LIMIT 10
        ''')
        result = db.session.execute(query)
        if len(result) < 1:
            response = {'supplier_name': "None",'total_balance': 0}
        else:
            response = []
            for row in result:
                response.append({
                    'supplier_name': row.supplier_name,
                    'total_balance': row.total_balance
                })
        return {'invoices': response}

@blp.route("/transaction/sales/credit")
class SalesCreditViews(MethodView):
    def get(self):
        query = text('''
            SELECT customers.customer_name, SUM(customer_balances.balance) AS total_balance
            FROM receipts
            JOIN customers ON receipts.customer_id = customers.id
            JOIN customer_balances ON receipts.customer_id = customer_balances.customer_id
            WHERE receipts.accounted_status = 'fully_accounted'
                AND receipts.status != 'fully paid'
                AND receipts.sale_type = 'credit'
            GROUP BY customers.customer_name, receipts.date
            ORDER BY total_balance ASC, receipts.date ASC
            LIMIT 10
        ''')
        result = db.session.execute(query)
        if len(result) < 1:
            response = {'customer_name': "None",'total_balance': 0}
        else:
            response = []
            for row in result:
                response.append({
                    'customer_name': row.customer_name,
                    'total_balance': row.total_balance
                })

        return {'receipts': response}
