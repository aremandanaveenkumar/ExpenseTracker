import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('ExpenseTracker')

monthlyexpenses = SHEET.worksheet('monthlyexpenses')

data = monthlyexpenses.get_all_values()

subcategories = SHEET.worksheet('subcategories')

headers = subcategories.col_values(1)

def get_categories():
    """
    ask user for a category and display sub categories
    """
    print('Choose a number for displaying sub categories if any : ')

    header_index = 0
    row_headers = subcategories.row_values(1)
    for header in row_headers:
        if header :
            print(f'{header} : {header_index}')
            header_index += 1
    
    selected = input("Select Category by inputing relevant Number :")
    selected_index = int(selected)
    if selected_index == 0:
        selected_index += 1
    elif selected_index > 0:
        selected_index += 2
    col_headers = subcategories.col_values(selected_index)
    print(col_headers)

    
get_categories()

    
