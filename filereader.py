import pandas as pd
import re
import constants
import openpyxl


def acquire_numbers_from_excel_file(file_name = "numeri.xls"):
    wb = pd.read_excel(file_name, header=None, engine="openpyxl")
    sheet = wb.to_numpy()
    correct_numbers = []
    wrong_number_indexes = []
    col_numbers = -1
    for i in range(0, sheet.shape[1]):
        if type(sheet[0, i]) == str:
            if check_if_number(sheet[0, i]):
                col_numbers = i
                break
    if col_numbers == -1:
        raise Exception(constants.no_numbers_in_excel_exception_str)
    for j in range(0, sheet.shape[0]):
        try:
            current_number = fix_number(sheet[j, col_numbers])
            correct_numbers.append(current_number)
        except:
            wrong_number_indexes.append(j)
    return correct_numbers, wrong_number_indexes


def check_if_number(to_check):
    return re.match(constants.check_number_regex, to_check)


def fix_number(to_fix):
    if not check_if_number(to_fix):
        raise Exception(constants.wrong_number_exception_str)
    to_fix = to_fix.replace(" ", "")
    where_plus = to_fix.rfind("+")
    if where_plus > 0 and re.match(constants.check_if_digit, to_fix[where_plus - 1]):
        raise Exception(constants.wrong_number_exception_str)
    num_digits = 0
    for i in range(0, len(to_fix)):
        if re.match(constants.check_if_digit, to_fix[i]):
            num_digits += 1
    if where_plus < 0:
        if num_digits == constants.num_digits_in_number:
            to_fix = "+39" + to_fix
        else:
            raise Exception(constants.wrong_number_exception_str)
    else:
        if num_digits - 2 != constants.num_digits_in_number:  # we exclude the number of digits in the prefix
            raise Exception(constants.wrong_number_exception_str)
    return to_fix



