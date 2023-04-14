@jwt_required(fresh=True)
@blp.arguments(PlainSalesSchema)
@blp.response(201, SalesSchema)
def post(self, data):
    item_in_stock = InventoryBalancesModel.query.filter_by(item_id=data["item_id"]).first()
    if not item_in_stock:
        abort(400, message="Item is not in stock! It might have never been bought!!")

    sale_item_quantity = db.session.query(db.func.sum(InventoryBalancesModel.quantity)).filter_by(
        item_id=data["item_id"]).scalar()
    if sale_item_quantity <= 0:
        abort(400, message="You do not have enough quantity")

    sale_items = InventoryBalancesModel.query.filter_by(item_id=data["item_id"]).order_by(
        InventoryBalancesModel.date).all()

    if sale_item_quantity >= data["quantity"]:
        remaining_qty = data["quantity"]
        for item in sale_items:
            if remaining_qty > 0:
                if item.quantity >= remaining_qty:
                    item.quantity -= remaining_qty
                    remaining_qty = 0
                else:
                    remaining_qty -= item.quantity
                    item.quantity = 0
            else:
                break
        sale_added = SalesModel(item_id=data["item_id"],
                                customer_id=data["customer_id"], currency=data["currency"],
                                quantity=data["quantity"],
                                sale_type=data["sale_type"],
                                selling_price=data["selling_price"])
        if data["sale_type"] == "cash":
            """cash sale"""
            sale_added.save_to_db()
            cash_account = AccountModel.query.filter_by(account_type="cash",
                                                        account_category="Sale Account").first()
            customer_account = sale_added.customer.account_id
            selling_price = sale_added.selling_price
            quantity = sale_added.quantity
            customer_id = sale_added.customer.id

            try:
                sales_accounting_transaction(sales_account_id=cash_account.id, sale_id=sale_added.id,
                                             customer_account_id=customer_account, selling_price=selling_price,
                                             quantity=quantity)
                add_customer_balance(customer_id=customer_id, sale_id=sale_added.id, receipt_amount=sale_added.amount)
                return sale_added
            except:
                traceback.print_exc()
                return {"message": "Could not create accounting"}
        else:
            sale_added.save_to_db()
            cash_account = AccountModel.query.filter_by(account_type="credit",
                                                        account_category="Sale Account").first()
            customer_account = sale_added.customer.account_id
            selling_price = sale_added.selling_price
            quantity = sale_added.quantity
            customer_id = sale_added.customer.id
            try:
                sales_accounting_transaction(sales_account_id=cash_account.id, sale_id=sale_added.id,
                                             customer_account_id=customer_account, selling_price=selling_price,
                                             quantity=quantity)
                add_customer_balance(customer_id=customer_id, sale_id=sale_added.id, receipt_amount=sale_added.amount)
                return sale_added
            except:
                traceback.print_exc()
                return {"message": "Could not create accounting"}
    else:
        abort(400, message="Sale has not be made, not enough quantity!!")