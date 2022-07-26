import gspread
from google.oauth2.service_account import Credentials
import math
import datetime

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]
CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("home-expenses-tracker")


def choose_worksheet():
    """
    Allow the user to choose the field to which the expense belongs
    or to access total worksheet.
    Show the spending of the current month and how much budget
    is left to be spent, if a budget was set.
    Run a while loop to collect a valid string from the user
    via terminal, which must be a string of 1 letter within the possible
    choices. The loop will repeatedly request data until it is valid.
    """
    try:
        current_month = int(datetime.datetime.today().month) + 1
        spent = SHEET.worksheet("total").col_values(current_month)
        budget = SHEET.worksheet("budget").col_values(current_month)

        def budget_left(row):
            try:
                num_spent = int(spent[row] if spent[row] != "" else "0")
                bgt_left = int(budget[row]) - num_spent
            except Exception:
                bgt_left = " unknown, budget not set."
            return bgt_left
        print(f"Please select what kind of operation you would like \
to perform:\n-Update a worksheet:\n Please select what \
kind of expense you are updating today:\n 1: Gas bill,\n 2: \
Electricity bill,\n 3: Water bill\
,\n 4: Council tax,\n 5: Rent/Mortgage,\n  This month: spent £{spent[1]}, \
budget left £{budget_left(1)}\n\n 6: Car expenses,\n\
  This month: spent £{spent[2]}, budget left £{budget_left(2)}\n\n\
 7: Food expenses;\n  This month: spent £{spent[3]}, \
budget left £{budget_left(3)}\n\n-Set a budget:\n 8: Set a monthly \
budget\n-View totals\n 9: View the totals of your monthly expenses.")
    except IndexError:
        print("Please select what kind of operation you would like \
to perform:\n-Update a worksheet:\n Please select what \
kind of expense you are updating today:\n 1: Gas bill,\n 2: \
Electricity bill,\n 3: Water bill,\n 4: Council tax,\n \
5: Rent/Mortgage,\n 6: Car expenses,\n 7: Food expenses;\n-Set a budget:\
\n 8: Set a monthly budget\n-View totals\n 9: View the totals of your \
monthly expenses.")
    while True:
        worksheet_choice = input("Input:\n")
        max_num_choices = 9
        if validate_choice(worksheet_choice, max_num_choices):
            break
    return worksheet_choice


def choose_month():
    """
    Allow the user to choose the month to update.
    Run a while loop to collect a valid string of data from the user
    via terminal, which must be a number within 1 and 12.
    The loop will repeatedly request data until it is valid.
    """
    print("Now choose the month for your operation.\
\n1: January,\n2: February,\n3: March,\n\
4: April,\n5: May,\n6: June,\n7: July,\n8: August,\
\n9: September,\n10: October,\n11: November,\
\n12: December\n")
    while True:
        month_choice = input("Input:\n")
        max_num_months = 12

        if validate_choice(month_choice, max_num_months):
            break
    return month_choice


def find_worksheet(chosen_worksheet_num):
    """
    Locate the worksheet that the user has chosen to update
    """
    if chosen_worksheet_num == "6":
        worksheet_name = "car"
    elif chosen_worksheet_num == "7":
        worksheet_name = "food"
    elif chosen_worksheet_num == "8":
        worksheet_name = "budget"
    else:
        worksheet_name = "monthly_bills"
    print(worksheet_name)
    return worksheet_name


def get_expense_data():
    """
    Get expense input from the user.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of a number.
    The loop will repeatedly request data until it is valid.
    """
    print("Please enter the value of your expense or \
budget,\ndepending on your previous choice.\
\nData should be a decimal or an integer \
number,\nwhich will be automatically approximated.\nExample: 109.08\n")
    while True:
        data = input("Enter your data here:\n")
        if validate_input_data(data):
            break
    data_num = math.ceil(float(data))
    return data_num


def update_worksheet(data, chosen_worksheet_num, column, worksheet_name):
    """
    With the data provided, update the relevant cell
    if the first choice was a monthly bill.
    Otherwise, update the first cell available of
    the chosen month column in the relevant worksheet.
    """
    chosen_worksheet = SHEET.worksheet(worksheet_name)
    if int(chosen_worksheet_num) <= 5:
        row = int(chosen_worksheet_num) + 1
        column = int(column) + 1
    else:
        row = len(chosen_worksheet.col_values(column)) + 1
    chosen_worksheet.update_cell(row, column, data)
    month_name = chosen_worksheet.row_values(1)[int(column) - 1]
    print(f"Your {worksheet_name} worksheet has been updated:\n\
The new value for {month_name} is: {data}.\n")


def totals_to_update(chosen_worksheet_num):
    """
    Assign the arguments to update monthly total
    function in base of the letter choice
    """
    print("Updating total worksheet...\n")
    if chosen_worksheet_num == "6":
        update_monthly_totals(1, "car", "B3")
        totals_of_totals()
    elif chosen_worksheet_num == "7":
        update_monthly_totals(1, "food", "B4")
        totals_of_totals()
    elif chosen_worksheet_num == "8":
        pass
    else:
        update_monthly_totals(2, "monthly_bills", "B2")
        totals_of_totals()


def calculate_totals(row, worksheet_name):
    """
    Add all values for each column in a worksheet and
    return the results as a list of list.
    """
    chosen_worksheet = SHEET.worksheet(worksheet_name)
    total_list_of_list = []
    total_list = []
    column_number = len(chosen_worksheet.row_values(1))
    for num in range(row, column_number + 1):
        column = chosen_worksheet.col_values(num)
        column.pop(0)
        int_column = [int(value if value != "" else "0") for value in column]
        totals = sum(int_column)
        total_list.append(totals)
    total_list_of_list.append(total_list)
    return total_list_of_list


def update_monthly_totals(row, worksheet_name, coordinate):
    """
    Update total worksheet with the new calculated totals
    in the respective row.
    """
    total_worksheet = SHEET.worksheet("total")
    updated_list = calculate_totals(row, worksheet_name)
    total_worksheet.update(coordinate, updated_list)


def totals_of_totals():
    """
    Clear the previous values in the Year Total column.
    Sum the values of each row in the total worksheet to view
    the yearly costs of each expense type.
    Update the Year Total column with the new values.
    """
    print("Updating year totals...\n")
    total_worksheet = SHEET.worksheet("total")
    total_worksheet.batch_clear(["N2:N4"])
    total_list = []
    for num in range(2, 5):
        row = total_worksheet.row_values(num)
        row.pop(0)
        int_row = [int(value if value != "" else "0") for value in row]
        totals = [sum(int_row)]
        total_list.append(totals)
    total_worksheet.update("N2:N4", total_list)

    print("Updating monthly totals...\n")
    total_worksheet.batch_clear(["B5:N5"])
    update_monthly_totals(2, "total", "B5")
    print("Your total worksheet is updated!\n")


def view_total_data():
    """
    Access the value of the Total Expenses for the selected month
    or the Year Total of an expense type.
    """
    total_type = choose_total()
    total_worksheet = SHEET.worksheet("total")
    if total_type == "1":
        month_total = choose_month()
        month_column = int(month_total) + 1
        row = len(total_worksheet.col_values(month_column))
        cell = total_worksheet.cell(row, month_column).value
        month_name = total_worksheet.cell(1, month_column).value
        print(f"The total of your expenses for {month_name} is:\n £{cell}")
    else:
        exp_year_total = choose_expense_type()
        requested_exp_type = total_worksheet.col_values(1)[int(exp_year_total)]
        requested_value = total_worksheet.col_values(14)[int(exp_year_total)]
        print(f"So far this year your {requested_exp_type} amount is:\n\
£{requested_value}")


def choose_total():
    """
    Allow the user to view the totals by month or expense type.
    Run a while loop to collect a valid string of data from the user
    via terminal, which must be a number within 1 and 2.
    The loop will repeatedly request data until it is valid.
    """
    print("Type 1:\n If you would like to view the total \
of your expenses by month;\nType 2:\n If you prefer \
to see how much you spent during this year so far,\nof an expense \
type such as food or monthly bills.")
    while True:
        total_choice = input("Input:\n")
        max_choices = 2
        if validate_choice(total_choice, max_choices):
            break
    return total_choice


def choose_expense_type():
    """
    Allow the user to choose the expense type.
    Run a while loop to collect a valid string of data from the user
    via terminal, which must be a number within 1 and 4.
    The loop will repeatedly request data until it is valid.
    """
    print("Now type which kind of expense you would like to view:\n\
1. Monthly Bills;\n2. Car Expenses\n3. Food Expenses;\n4. Total Expenses\n")
    while True:
        expense_type = input("Input:\n")
        max_types = 4
        if validate_choice(expense_type, max_types):
            break
    expense_type_num = int(expense_type)
    return expense_type_num


def calculate_total_budget(column, tot_index):
    """
    If the cell for the relative month of the Total Expense
    (in the budget worksheet) is empty,
    try to update it by adding all the values in the column.
    If not possible, handle the error by printing a message
    for the user explaining how to fix the issue.
    """
    month_column = int(column) + 1
    budget_worksheet = SHEET.worksheet("budget")
    budget_column = budget_worksheet.col_values(month_column)
    row_num = tot_index + 1
    try:
        budget_column[tot_index]
    except IndexError:
        try:
            budget_column.pop(0)
            int_column = [int(value) for value in budget_column]
            if len(int_column) == 3:
                budget_tot = sum(int_column)
                budget_worksheet.update_cell(row_num, month_column, budget_tot)
            else:
                raise ValueError
        except ValueError:
            print("You haven't set all expenses budgets for this month.\n\
Total budget for this month can't be calculated.\n")


def ind_rows_to_compare(chosen_worksheet_num):
    """
    Depending on the worksheet chosen, pick the row for total
    and budget worksheets that compare_budget function will compare.
    """
    if int(chosen_worksheet_num) <= 5:
        ind_row = 1
    elif int(chosen_worksheet_num) == 6:
        ind_row = 2
    else:
        ind_row = 3
    return ind_row


def compare_budgets(column, ind_row):
    """
    Access the total values of the expense updated and the expense budget.
    Subtract the values and print a message to the user.
    The message compares the values and states the discrepancy.
    Handle any error if the subtraction is impossible
    by printing feedback in the terminal.
    """
    month_column = int(column) + 1
    total_worksheet = SHEET.worksheet("total")
    budget_worksheet = SHEET.worksheet("budget")
    month_name = budget_worksheet.col_values(month_column)[0]
    expense_name = budget_worksheet.col_values(1)[ind_row]
    try:
        tot_value = total_worksheet.col_values(month_column)[ind_row]
        budget = budget_worksheet.col_values(month_column)[ind_row]
        if int(tot_value) <= int(budget):
            difference = int(budget) - int(tot_value)
            print(f"Congratulations!\n \
For {month_name} your {expense_name} are still in the budget!\n\
You are £{difference} far from exceeding your {expense_name} budget!\n")
        else:
            difference = int(tot_value) - int(budget)
            print(f"Unfortunately, for {month_name}\nyour {expense_name} \
exceeded your budget of £{difference}.\n")
    except Exception:
        print(f"You don't have a total or a budget for\nthe {expense_name} in \
{month_name}.\n")


def exit_restart():
    """
    Request the user to choose between exiting
    the app or continuing with a new operation.
    Run a while loop to collect a valid string of data from the user
    via terminal, which must be a string with value y or n.
    The loop will repeatedly request data until it is valid.
    """
    while True:
        print("Do you wish to continue with another operation?")
        last_input = input("Input y for yes or n for no\n").lower()
        choice_options = ("y", "n")
        if validate_last_choice(last_input, choice_options):
            break
    return last_input


def validate_choice(choice, max_num):
    """
    Inside the try, state that the value must be in a specific range.
    Raise a value error if the string value is not convertible
    into an integer or if it is outside the range.
    """
    try:
        choice_number = int(choice)
        if choice_number < 1 or choice_number > max_num:
            raise ValueError(
                f"Only values between 1 and {max_num} are acceptable,\n\
you entered: {choice}"
                )
    except ValueError as e:
        print(f"Invalid data: {e}.\nPlease try again.\n")
        return False

    return True


def validate_input_data(value):
    """
    Inside the try, convert the string value into an approximated integer.
    Raises ValueError if the string is not convertible into an integer.
    """
    try:
        if float(value) >= 0:
            math.ceil(float(value))
        else:
            raise ValueError(
                "Your value can't be a negative number"
            )
    except ValueError as e:
        print(f"Invalid data: {e}.\nPlease try again.\n")
        return False
    return True


def validate_last_choice(value, possible_choice):
    """
    Inside the try, state that the value must be included
    in possible choice.
    Raise a value error if the value is not exactly 1
    or if it's not correct.
    """
    try:
        if value in possible_choice:
            if len(value) != 1:
                raise ValueError(
                    f"Only 1 value is required,\nyou entered {len(value)} \
values.")
        else:
            raise ValueError(
                f"You have input {value};\nyour value must be either y or n"
                )
    except ValueError as e:
        print(f"invalid data: {e}.\nPlease try again.\n")
        return False

    return True


def main():
    """
    Run all program functions depending on the chosen operation
    """
    worksheet_num = choose_worksheet()
    if worksheet_num == "9":
        view_total_data()
    elif worksheet_num == "8":
        exp_type = choose_expense_type()
        worksheet_to_update = find_worksheet(worksheet_num)
        month = choose_month()
        expense = get_expense_data()
        update_worksheet(expense, exp_type, month, worksheet_to_update)
        compare_budgets(month, exp_type)
        monthly_tot_index = 4
        if exp_type != monthly_tot_index:
            calculate_total_budget(month, monthly_tot_index)
            compare_budgets(month, monthly_tot_index)
    else:
        worksheet_to_update = find_worksheet(worksheet_num)
        month = choose_month()
        expense = get_expense_data()
        update_worksheet(expense, worksheet_num, month, worksheet_to_update)
        totals_to_update(worksheet_num)
        rows_index = ind_rows_to_compare(worksheet_num)
        compare_budgets(month, rows_index)
        monthly_tot_index = 4
        calculate_total_budget(month, monthly_tot_index)
        compare_budgets(month, monthly_tot_index)
    last_choice = exit_restart()
    if last_choice == "y":
        main()
    else:
        print("Have a great day!\nSee you next time!")


print("Welcome to your Home Expense Tracker!\n")
main()
