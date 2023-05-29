from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font

data = {
    "Joe": {
        "math": 65,
        "science": 78,
        "english": 98,
        "gym": 89
    },
    "Bill": {
        "math": 55,
        "science": 72,
        "english": 87,
        "gym": 95
    },
    "Tim": {
        "math": 100,
        "science": 45,
        "english": 75,
        "gym": 92
    },
    "Sally": {
        "math": 30,
        "science": 25,
        "english": 45,
        "gym": 100
    },
    "Jane": {
        "math": 100,
        "science": 100,
        "english": 100,
        "gym": 60
    }
}

# Create a workbook object

wb = Workbook()

# Create a worksheet

ws = wb.active
ws.title = "Grades"
headings = ["Name"] + list(data['Joe'].keys())
ws.append(headings)

for person in data:
    grades = data[person].values()
    ws.append([person] + list(grades))

for col in range(2, len(data['Joe'])+2):
    char = get_column_letter(col)
    ws[char + "7"] = f"=SUM({char+'2'}:{char+'6'})/{len(data)}"

for col in range(1, 6):
    ws[get_column_letter(col) + '1'].font = Font(bold=True, color="FF0000", italic=True)

wb.save('new_grades.xlsx')


# load exisiting spreadsheet

wbook = load_workbook("C:/Users/Public/Downloads/dmzee/book1.xlsx")

wsheet = wbook['Items']

for row in range(1, 10):
    for col in range(1, 4):
        char = get_column_letter(col)
        # print(wsheet[char + str(row)].value)
        # print(char + str(row))

# wsheet.merge_cells("A1:C1")
# wsheet.unmerge_cells("A1:C1")
# wsheet.insert_rows(3)
# wsheet.delete_rows(3)
# wsheet.insert_cols(2)
# wsheet.delete_cols(2)
#wsheet.move_range("A1:C9", rows=2, cols=2)
#wbook.save("C:/Users/Public/Downloads/dmzee/book1.xlsx")

# print(f"{wsheet['A2'].value}-{wsheet['A3'].value}")
# Grab a whole column
# returns tuples
# column_a = wsheet['A']
# row_1 = wsheet['1']

# save changes..the excell should be open

wsheet['A2'].value = "Screw Driver"

# wbook.save("C:/Users/Public/Downloads/dmzee/book1.xlsx")

# accessing sheetnames

sheetnames = wbook.sheetnames
active_ws = wbook['Categories']
# print(active_ws)

create_sheet = 'Test'
wbook.create_sheet(create_sheet)
# wbook.save("C:/Users/Public/Downloads/dmzee/book1.xlsx")
# print(sheetnames)

wbook_2 = Workbook()
wsheet_2 = wbook_2.active
wsheet_2.title = 'Data'

wsheet_2.append(["Muga", "Is", "Learning", "Excel"])  # adds to the end

# wbook_2.save("Test.xlsx")
