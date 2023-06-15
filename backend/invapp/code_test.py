import pandas as pd
import openpyxl

from backend.invapp.models.masters.accountsmodel import AccountModel

def upload_data():
    data = pd.read_excel("hardware_items.xlsx", sheet_name="CATEGORY_ACCOUNT")
    for index, row in data.iterrows():
        account = AccountModel(account_name=row["ACCOUNT_NAME"], account_number=row["ACCOUNT_NUMBER"], account_description=row["ACCOUNT_DESCRIPTION"])
        account.save_to_db()
    print(f"{len(data)} added successfully")

upload_data()
