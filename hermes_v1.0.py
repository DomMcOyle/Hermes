import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import xlrd
import os.path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

wa_button_send_id = "_4sWnG"


def initialize_web_driver():
    homedir = os.path.expanduser("~")
    op = Options()
    op.add_argument("--user-data-dir=" + homedir + "\\AppData\\Local\\Google\\Chrome\\User Data")
    op.add_experimental_option("excludeSwitches", ["enable-automation"])
    op.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome("chromedriver_win32//chromedriver.exe",
                              options=op)
    driver.maximize_window()
    return homedir, op, driver


def wa_send(driver):
    driver.find_element_by_xpath("//span[@data-icon='send']").click()
    time.sleep(2)


def send_to_list(list_of_numbers, text_list):
    homedir, op, driver = initialize_web_driver()
    for i in range(0, len(list_of_numbers)):
        driver.get("https://web.whatsapp.com/send?phone=" + list_of_numbers[i] + "&text=" + text_list[i])
        time.sleep(8)
        wa_send(driver)
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


def send_img():
    homedir, op, driver = initialize_web_driver()
    filepath = "C:\\Users\\GiovanniPio\\Desktop\\programmi vari\\point clouds\\bidone\\bidone00001.jpg"
    dodo = "+393466296727"
    clipboard_button = "_2jitM"
    send = "_165_h _2HL9j"
    text = "smegmabottle"

    driver.get("https://web.whatsapp.com/send?phone=" + dodo + "&text=" + text)
    time.sleep(5)
    driver.find_element_by_class_name(clipboard_button).click()
    #time.sleep(1)
    inv = driver.find_element_by_xpath("//input[@type='file']")
    inv.send_keys(filepath)
    time.sleep(3)
    #driver.find_elements_by_class_name(send)[0].click()
    wa_send(driver)




send_img()


"""
some saved urls

#driver.get("https://www.google.com/search?q=lala&oq=lala&aqs=chrome..69i57.423j0j9&sourceid=chrome&ie=UTF-8")
#driver.get("https://web.whatsapp.com/")
#driver.find_element_by_class_name(cname).send_keys(Keys.control() + "v")
"""