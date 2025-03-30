import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

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


def clear_old_entries():
    """
    clear yesterday entries from sub categories columns
    """
    row_headers = subcategories.row_values(1)
    for i in range(2, len(row_headers) + 2, 2):
        colC = chr(i + 64)
        cols = subcategories.range(colC + '1' + ':' + colC + '12')
        for col in cols:
            col.value = ''
        subcategories.update_cells(cols)


def get_last_modified():
    """
    get the date of the file last modified
    if it is not today then clear all old
    entries from the worksheet subcategories
    """
    fid = SHEET.id
    drive = build('drive', 'v3', credentials=CREDS)
    file_md = drive.files().get(fileId=fid, fields='modifiedTime').execute()
    last_modified_time = file_md.get('modifiedTime')
    return last_modified_time


def get_categories():
    """
    ask user for a category and display sub categories
    """
    print('Choose a number for displaying sub categories if any : ')

    header_index = 0
    row_headers = subcategories.row_values(1)
    for header in row_headers:
        if header:
            print(f'{header} : {header_index}')
            header_index += 1

    selected = input("Select Category by inputing relevant Number :")
    validate_input(selected)
    selected_index = int(selected)
    if selected_index == 0:
        selected_index += 1
    elif selected_index > 0:
        selected_index += 2
    col_headers = subcategories.col_values(selected_index)
    colheader_index = 0
    for colheader in col_headers:
        if colheader:
            print(f'{colheader} : {colheader_index}')
            colheader_index += 1
    selected_col = input("Select Sub Category by inputing relevant Number :")
    validate_input(selected_col)
    # selected_colindex = int(selected_col)


def validate_input(input_value):
    """
    validate input from user
    """
    try:
        if not input_value:
            raise ValueError(
                " Input is empty "
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")


def main():
    modified = datetime.strptime(get_last_modified(), '%Y-%m-%dT%H:%M:%S.%fZ')
    today = datetime.today()
    if modified.date() != today.date():
        clear_old_entries()


main()
