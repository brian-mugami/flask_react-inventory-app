from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font

def upload_data():
    data = pd.read_excel("stock_holding_report_06_02_2023.xlsx")
    print(len(data)-1)
    for index, row in data.iterrows():
        print(index)

upload_data()
