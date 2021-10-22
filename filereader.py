import xlrd
import re

check_number_regex = "^([0-9]|\s|\+)+$"
wrong_number_exception_str = "wrong number exception"
no_numbers_in_excel_exception_str = "no numbers in excel file"
check_if_digit = "[0-9]"
num_digits_in_number = 10


def acquire_numbers_from_excel_file(file_name = "numeri.xls"):
    wb = xlrd.open_workbook(file_name)
    sheet = wb.sheet_by_index(0)
    correct_numbers = []
    wrong_number_indexes = []
    col_numbers = -1
    for i in range(0, sheet.ncols):
        if check_if_number(sheet.cell_value(0, i)):
            col_numbers = i
            break
    if col_numbers == -1:
        raise Exception(no_numbers_in_excel_exception_str)
    for j in range(0, sheet.nrows):
        try:
            current_number = fix_number(sheet.cell_value(j, col_numbers))
            correct_numbers.append(current_number)
        except:
            wrong_number_indexes.append(j)
    return correct_numbers, wrong_number_indexes


def check_if_number(to_check):
    return re.match(check_number_regex, to_check)


def fix_number(to_fix):
    if not check_if_number(to_fix):
        raise Exception(wrong_number_exception_str)
    to_fix = to_fix.replace(" ", "")
    where_plus = to_fix.rfind("+")
    if where_plus > 0 and re.match(check_if_digit, to_fix[where_plus - 1]):
        raise Exception(wrong_number_exception_str)
    num_digits = 0
    for i in range(0, len(to_fix)):
        if re.match(check_if_digit, to_fix[i]):
            num_digits += 1
    if where_plus < 0:
        if num_digits == num_digits_in_number:
            to_fix = "+39" + to_fix
        else:
            raise Exception(wrong_number_exception_str)
    else:
        if num_digits - 2 != num_digits_in_number:  # we exclude the number of digits in the prefix
            raise Exception(wrong_number_exception_str)
    return to_fix



