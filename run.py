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

subcategories = SHEET.worksheet('subcategories')

dailysummary = SHEET.worksheet('dailysummary')

headers = subcategories.col_values(1)

row_headers = subcategories.row_values(1)


def clear_daily_entries():
    """
    clear yesterday entries from sub categories columns
    add new 0 valued row in daily summary
    """

    rowvalues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(2, len(row_headers) + 2, 2):
        colC = chr(i + 64)
        cols = subcategories.range(colC + '1' + ':' + colC + '12')
        for col in cols:
            col.value = 0
        subcategories.update_cells(cols)
    dailysummary.append_row(rowvalues)


def clear_daily_summary(present_month):
    """
    clear entries in dailysummary sheet
    if last modified month is not equal
    to present month
    """

    first_row = dailysummary.row_values(1)
    dailysummary.clear()
    dailysummary.append_row(first_row)
    monthly_data = monthlyexpenses.get_all_values()
    rowdata = monthly_data[-1]
    month = int(rowdata[0])
    if month != present_month:
        rowvalues = [present_month, 0, 0, 0]
        monthlyexpenses.append_row(rowvalues)


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
    selected = validate_input(selected)
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
    selected = validate_input(selected)
    print("\033[H\033[J", end="")
    selected_index = int(selected)
    if selected_index == 0:
        selected_indices.append(99)
        print('Selection is InValid!')
        return selected_indices
    elif selected_index == 1:
        selected_indices.append(99)
        print('Selection : 1 is not Valid. This is Updated Automatically')
        return selected_indices
    elif selected_index > len(col_headers):
        selected_indices.append(99)
        print('Selection is InValid!')
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
        val = int(input_value)
        return input_value
    except ValueError:
        return "0"


def update_column_total(idx):
    """
    update first column with total of cells below in subcategories
    update last row with totals in daily summary
    update last row with totals and calculate balance in monthly expenses
    """
    total = 0
    col_values = subcategories.col_values(idx[0] + 1)
    for ind in range(1, len(col_values)):
        total += int(col_values[ind])
    rowChar = chr(idx[0] + 65)
    cell_label = f'{rowChar}1'
    subcategories.update_acell(cell_label, total)
    monthly_data = monthlyexpenses.get_all_values()
    daily_data = dailysummary.get_all_values()
    rowdata = monthly_data[-1]
    rowvalues = []
    row_headers = subcategories.row_values(1)
    for i in range(2, len(row_headers) + 2, 2):
        rowvalues.append(row_headers[i-1])
    row_count = len(daily_data)
    cell_list = dailysummary.range(f'A{row_count}:L{row_count}')
    for cell, data in zip(cell_list, rowvalues):
        cell.value = data
    dailysummary.update_cells(cell_list)
    row_count = len(daily_data)
    cell_list = dailysummary.range(f'A2:L{row_count}')
    expenditure = 0
    balance = 0
    for cell in cell_list:
        expenditure += int(validate_input(cell.value))
    rowdata[2] = expenditure
    balance = int(rowdata[1]) - expenditure
    rowdata[3] = balance
    row_count = len(monthly_data)
    cell_list = monthlyexpenses.range(f'A{row_count}:D{row_count}')
    for cell, data in zip(cell_list, rowdata):
        cell.value = data
    monthlyexpenses.update_cells(cell_list)


def main():
    modified = datetime.strptime(get_last_modified(), '%Y-%m-%dT%H:%M:%S.%fZ')
    today = datetime.today()
    present_month = today.month
    modified_month = modified.month
    if present_month != modified_month:
        clear_daily_summary(present_month)
    if modified.date() != today.date():
        clear_daily_entries()
    while True:
        print('')
        print("Get Budget For this Month : 20")
        print("Set Budget For this Month : 30")
        print("Get Expenditure For this Month : 40")
        print("Get Balance For this Month : 50")
        print("Get Daily Summary : 60")
        print("Get Daily Summary for a Category : 70")
        print("Set How much you spent for a Sub Category : 80")
        print("Do Nothing! Just Exit : 100")
        option_in = input("Select by inputing relevant Number : ")
        option = validate_input(option_in)
        print("\033[H\033[J", end="")
        monthly_data = monthlyexpenses.get_all_values()
        daily_data = dailysummary.get_all_values()
        if (int(option) == 20):
            rowdata = monthly_data[-1]
            print(f"Budget is : {rowdata[1]}")
        elif (int(option) == 30):
            rowdata = monthly_data[-1]
            budget_input = input("Set Budget to : ")
            budget_in = validate_input(budget_input)
            budget = int(budget_in)
            if budget > 0:
                rowdata[1] = budget
                row_count = len(monthly_data)
                cell_list = monthlyexpenses.range(f'A{row_count}:D{row_count}')
                for cell, data in zip(cell_list, rowdata):
                    cell.value = data
                monthlyexpenses.update_cells(cell_list)
                print("Budget Set. Sheet is Updated!")
            else:
                print(f' input : {budget_input} is invalid Input!')
        elif (int(option) == 40):
            rowdata = monthly_data[-1]
            print(f"Expenditure is : {rowdata[2]}")
        elif (int(option) == 50):
            rowdata = monthly_data[-1]
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
                amount_in = input(f'Amount Spent For {idx[2]} : ')
                amount = validate_input(amount_in)
                if int(amount) > 0:
                    subcategories.update_acell(cell_label, amount)
                    update_column_total(idx)
                    print('Sheet Updated!')
                else:
                    print(f' input : {amount_in} is invalid Input!')
        elif (int(option) == 100):
            print("\033[H\033[J", end="")
            break
        else:
            print(f' input : {option_in} is an Invalid Input! Try Again.')


main()
