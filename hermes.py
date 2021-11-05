import time
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.options import Options
#import xlrd
import os.path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from filereader import acquire_numbers_from_excel_file
import threading
import traceback
import psutil


def initialize_web_driver():
    homedir = os.path.expanduser("~")
    op = Options()
    op.add_argument("--user-data-dir=" + homedir + "\\AppData\\Local\\Google\\Chrome\\User Data")
    op.add_experimental_option("excludeSwitches", ["enable-automation"])
    op.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome("chromedriver.exe",
                              options=op)
    driver.maximize_window()
    return homedir, op, driver


def wa_send(driver, string_of_photos):
    if string_of_photos:
        clipboard_button = "_2jitM"
        driver.find_element_by_class_name(clipboard_button).click()
        inv = driver.find_element_by_xpath("//input[@type='file']")
        inv.send_keys(string_of_photos)
    time.sleep(1)
    driver.find_element_by_xpath("//span[@data-icon='send']").click()
    time.sleep(1)


def send_to_list(list_of_numbers, start_idx,  text_list, list_of_photos, window):
    homedir, op, driver = initialize_web_driver()

    string_of_photos = ""
    if len(list_of_photos) > 0:
        string_of_photos = list_of_photos[0]
        for photo in range(1, len(list_of_photos)):
            string_of_photos += ('\n' + list_of_photos[photo])

    print("effective range: " + str(range(start_idx, len(list_of_numbers))))
    incremental_sleep = 2
    for i in range(start_idx, len(list_of_numbers)):
        try:
            time.sleep(incremental_sleep)
            driver.get("https://web.whatsapp.com/send?phone=" + list_of_numbers[i] + "&text=" + text_list)
            time.sleep(incremental_sleep)
            wa_send(driver, string_of_photos)
        except:
            i -= 1
            if incremental_sleep < 8: # da lanciare l'eccezione se aspetta troppo -- TIMEOUT
                incremental_sleep += 1
            time.sleep(incremental_sleep)
            traceback.print_exc()
        window.update_progress_bar()
    driver.close()
    window.finalize()


def send_to_list_in_thread(list_of_numbers, start_idx,  text_list, list_of_photos, window):
    threading.Thread(target=send_to_list,
                     args=(list_of_numbers, start_idx,  text_list, list_of_photos, window),
                     daemon=True).start()


def check_if_open(exename = 'chrome.exe'):
    for proc in psutil.process_iter(['pid', 'name']):
        # This will check if there exists any process running with executable name
        if proc.info['name'] == exename:
            return True
    return False

"""
def send_img():
    homedir, op, driver = initialize_web_driver()
    filepath = "C:\\Users\\Neo Dom-Z Mk. II\\Desktop\\repo hermes\\Hermes\\place_holder_donore_come_manfredi.png"\
               + '\n' + "C:\\Users\\Neo Dom-Z Mk. II\\Desktop\\repo hermes\\Hermes\\place_holder_donore_come_manfredi.png"
    dodo = "+393466296727"
    clipboard_button = "_2jitM"
    send = "_165_h _2HL9j"
    text = ""

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

"""
some saved urls

#driver.get("https://www.google.com/search?q=lala&oq=lala&aqs=chrome..69i57.423j0j9&sourceid=chrome&ie=UTF-8")
#driver.get("https://web.whatsapp.com/")
#driver.find_element_by_class_name(cname).send_keys(Keys.control() + "v")
"""