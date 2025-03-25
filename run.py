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

    row_headers = subcategories.row_values(1)
    header_index = 0

    for header in row_headers:
        print(f'{header} : {header_index}')
        header_index += 1
    
    selected_index = input("Select Category by inputing relevant Number :")
    print(row_headers[int(selected_index)])

    

get_categories()






