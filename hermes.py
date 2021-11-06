import time
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.options import Options
import os.path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import threading
import traceback
import psutil
from datetime import datetime
import chromedriver_autoinstaller

TIMEOUT = 30
NUM_NOT_FOUND_ALERT = "_20C5O _2Zdgs"


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
        wait_until(driver, "//span[@data-icon='clip']")
        driver.find_element_by_xpath("//span[@data-icon='clip']").click()
        inv = driver.find_element_by_xpath("//input[@type='file']")
        inv.send_keys(string_of_photos)
    wait_until(driver, "//span[@data-icon='send']")
    driver.find_element_by_xpath("//span[@data-icon='send']").click()
    time.sleep(1)
    wait_until(driver, "//span[@data-icon='msg-time']", disappears=True)


def send_to_list(list_of_numbers, start_idx,  text_list, list_of_photos, window):
    homedir, op, driver = initialize_web_driver()
    inexistent_numbers = []

    string_of_photos = ""
    if len(list_of_photos) > 0:
        string_of_photos = list_of_photos[0]
        for photo in range(1, len(list_of_photos)):
            string_of_photos += ('\n' + list_of_photos[photo])

    print("effective range: " + str(range(start_idx, len(list_of_numbers))))
    incremental_sleep = 2
    update = True
    for i in range(start_idx, len(list_of_numbers)):
        if window.get_kill_thread_value():
            window.rollback(i)
            return
        while window.get_pause_thread_value():
            if window.get_kill_thread_value():
                window.rollback(i)
                return
            time.sleep(1)
        try:
            driver.get("https://web.whatsapp.com/send?phone=" + list_of_numbers[i] + "&text=" + text_list)
            time.sleep(incremental_sleep)
            if len(driver.find_elements(By.CLASS_NAME, NUM_NOT_FOUND_ALERT)) > 0:
                inexistent_numbers.append([i, list_of_numbers[i]])
                update = True
            else:
                wa_send(driver, string_of_photos)
                update = True
        except:
            i -= 1
            if incremental_sleep < TIMEOUT: # da lanciare l'eccezione se aspetta troppo -- TIMEOUT
                incremental_sleep += 1
            time.sleep(incremental_sleep)
            traceback.print_exc()
        if update:
            window.update_progress_bar()
            if incremental_sleep > 2:
                incremental_sleep -= 1
    driver.close()
    not_found_warning = False
    if len(inexistent_numbers) > 0:
        print(inexistent_numbers)
        not_found_warning = True
        dump_inexistent_numbers(inexistent_numbers)

    window.finalize_send(not_found_warning)



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


def wait_until(driver, x_path_string, disappears=False):
    i = TIMEOUT
    if not disappears:
        while i > 0 and len(driver.find_elements(By.XPATH, x_path_string)) == 0:
            time.sleep(1)
            i -= 1
    else:
        while i > 0 and len(driver.find_elements(By.XPATH, x_path_string)) > 0:
            time.sleep(1)
            i -= 1


def dump_inexistent_numbers(number_list):
    f = open("Numeri inesistenti " + str(datetime.now().date()) + ".txt", mode="a")
    f.write("Indice\t\tNumero di telefono\n")
    for number in number_list:
        f.write(str(number[0]+1) + '\t\t' + str(number[1]) + '\n')
    f.close()


def update_driver():
    print(chromedriver_autoinstaller.install())



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