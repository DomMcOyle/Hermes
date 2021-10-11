import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import xlrd
import os.path

"""
def send_alternating(number, text):
    driver.get("https://web.whatsapp.com/send?phone=" + number + "&text=" + text)
    time.sleep(10)
    driver.find_element_by_class_name(button_class_name).click()
    time.sleep(2)"""


def send_to_list(list_of_numbers, text_list):
    button_class_name = "_4sWnG"
    homedir = os.path.expanduser("~")
    op = Options()
    op.add_argument("--user-data-dir="+homedir+"\\AppData\\Local\\Google\\Chrome\\User Data")
    op.add_experimental_option("excludeSwitches", ["enable-automation"])
    op.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome("chromedriver_win32//chromedriver.exe",
                              options=op)
    driver.maximize_window()
    for i in range(0, len(list_of_numbers)):
        driver.get("https://web.whatsapp.com/send?phone=" + list_of_numbers[i] + "&text=" + text_list[i])
        time.sleep(8)
        driver.find_element_by_class_name(button_class_name).click()
        time.sleep(2)
    driver.close()


def acquire_numbers_and_text_from_excel_file(file_name = "numeri.xls"):
    wb = xlrd.open_workbook(file_name)
    sheet = wb.sheet_by_index(0)
    numbers = []
    texts = []
    for i in range(0, sheet.nrows):
        numbers.append(sheet.cell_value(i, 0))
        texts.append(sheet.cell_value(i, 1))
    return numbers, texts


l_of_numbers, text_list = acquire_numbers_and_text_from_excel_file()
send_to_list(list_of_numbers=l_of_numbers, text_list=text_list)


