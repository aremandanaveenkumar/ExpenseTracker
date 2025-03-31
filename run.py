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

dailysummary = SHEET.worksheet('dailysummary')

daily_data = dailysummary.get_all_values()

headers = subcategories.col_values(1)

row_headers = subcategories.row_values(1)


def clear_old_entries():
    """
    clear yesterday entries from sub categories columns
    """

    for i in range(2, len(row_headers) + 2, 2):
        colC = chr(i + 64)
        cols = subcategories.range(colC + '1' + ':' + colC + '12')
        for col in cols:
            col.value = 0
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
    print('Choose a number for displaying Categories : ')
    for i in range(1, len(row_headers), 2):
        print(f'{row_headers[i - 1]} : {i}')
    print('Return To Main Menu : 99')
    selected = input("Select Category by inputing relevant Number :")
    validate_input(selected)
    selected_index = int(selected)
    if selected_index % 2 == 0 or selected_index > len(row_headers):
        return 99
    else:
        return selected_index
    # if selected_index == 0:
    #     selected_index += 1
    # elif selected_index > 0:
    #     selected_index += 2


def get_sub_categories():
    """
    return sub category index for entering value
    """
    selected_indices = []
    rowindex = get_categories()
    if rowindex == 99:
        selected_indices.append(99)
        print('Selection is InValid!')
        return selected_indices
    col_headers = subcategories.col_values(rowindex)
    header_index = 1
    for header in col_headers:
        print(f"{header} : {header_index}")
        header_index += 1
    print('Return To Main Menu : 99')
    selected = input("Select SubCategory by inputing relevant Number :")
    validate_input(selected)
    print("\033[H\033[J", end="")
    selected_index = int(selected)
    if selected_index > len(col_headers):
        selected_indices.append(99)
        print('Selection is InValid!')
        return selected_indices
    elif selected_index == 1:
        selected_indices.append(99)
        print('Selection : 1 is not Valid. This is Updated Automatically')
        return selected_indices
    selected_indices.append(rowindex)
    selected_indices.append(selected_index - 1)
    selected_indices.append(col_headers[selected_index - 1])
    return selected_indices


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
    while True:
        print('')
        print("Set Budget For this Month : 30")
        print("Get Expenditure For this Month : 40")
        print("Get Balance For this Month : 50")
        print("Get Daily Summary : 60")
        print("Get Daily Summary for a Category : 70")
        print("Set How much you spent for a Sub Category : 80")
        print("Do Nothing! Just Exit : 100")
        option = input("Select by inputing relevant Number : ")
        validate_input(option)
        print("\033[H\033[J", end="")
        if (int(option) == 30):
            rowdata = data[-1]
            print(f"Budget is : {rowdata[1]}")
        elif (int(option) == 40):
            rowdata = data[-1]
            print(f"Expenditure is : {rowdata[2]}")
        elif (int(option) == 50):
            rowdata = data[-1]
            print(f"Balance is : {rowdata[3]}")
        elif (int(option) == 60):
            print("Daily Summary is : ")
            headerdata = daily_data[0]
            rowdata = daily_data[-1]
            for header, headerval in zip(headerdata, rowdata):
                print(f"{header} : {headerval}")
        elif (int(option) == 70):
            idx = get_categories()
            if idx > 0 and idx <= len(row_headers):
                col_headers = subcategories.col_values(idx)
                col_values = subcategories.col_values(idx + 1)
                for header, headerval in zip(col_headers, col_values):
                    print(f'{header} : {headerval}')
        elif (int(option) == 80):
            idx = get_sub_categories()
            if len(idx) == 3 and idx[1] <= len(row_headers):
                rowChar = chr(idx[0] + 65)
                cell_label = f'{rowChar}{idx[1] + 1}'
                print("\033[H\033[J", end="")
                amount = input(f'Amount Spent For {idx[2]} : ')
                validate_input(amount)
                subcategories.update_acell(cell_label, amount)
        elif (int(option) == 100):
            print("\033[H\033[J", end="")
            break
        else:
            print('Invalid Input! Try Again.')


main()
