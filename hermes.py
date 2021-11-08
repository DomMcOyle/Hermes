import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
import os.path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import threading
import traceback
import psutil
from datetime import datetime
import chromedriver_autoinstaller

import constants
from alert import Alert, TimeoutException
from debug import Log



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


def send_to_list(list_of_numbers, wrong_num_idx, start_idx,  text_list, list_of_photos, window):
    i = start_idx
    num_wrong_index = 0
    try:
        homedir, op, driver = initialize_web_driver()
        # controllo d'accesso (non mi viene un'idea migliore)
        driver.get("https://web.whatsapp.com")  # apri whatsapp
        wait_until(driver, "//div[@aria-label='Scan me!']", disappears=True, exc=constants.except_message_qr)
        wait_until(driver, "//div[@id='side']")
        inexistent_numbers = []

        string_of_photos = ""
        if len(list_of_photos) > 0:
            string_of_photos = list_of_photos[0]
            for photo in range(1, len(list_of_photos)):
                string_of_photos += ('\n' + list_of_photos[photo])
        total_rows = len(list_of_numbers) + len(wrong_num_idx)

        for i in range(start_idx, total_rows):
            if window.get_kill_thread_value():
                window.rollback(i)
                return
            while window.get_pause_thread_value():
                if window.get_kill_thread_value():
                    window.rollback(i)
                    return
                time.sleep(1)
            if i not in wrong_num_idx:
                driver.get("https://web.whatsapp.com/send?phone=" + list_of_numbers[i-num_wrong_index] + "&text=" + text_list) #lancia
                wait_until(driver, "//div[@id='side']")
                if len(driver.find_elements(By.XPATH, "//*[contains(text(), 'via url non valido')]")) > 0:
                    inexistent_numbers.append([i, list_of_numbers[i-num_wrong_index]])

                else:
                    wa_send(driver, string_of_photos)
            else:
                inexistent_numbers.append([i, "Numero incorretto."])
                num_wrong_index = num_wrong_index + 1

            window.update_progress_bar()
        driver.close()
        not_found_warning = False
        if len(inexistent_numbers) > 0:
            not_found_warning = True
            dump_inexistent_numbers(inexistent_numbers)

        window.finalize(not_found_warning)
    except WebDriverException as e:
        if e.msg == "chrome not reachable":
            Alert().fire("Chrome non raggiungibile.\nSe è stato chiuso premere nuovamente \"Invia\"", "Errore")
            window.rollback(i)
        else:
            Alert().fire("Errore durante l'invio.\nControllare il file di log per maggiori dettagli", "Errore")
            Log(e)
    except TimeoutException as te:
        if te.msg == constants.except_message_timeout_reached:
            Alert().fire("Errore durante l'invio, controlla la connessione di rete e riprova", "Errore")
            window.rollback(i)
        elif te.msg == constants.except_message_qr:
            Alert().fire("Tempo per l'autenticazione (QR code) scaduto, esegui l'accesso e riprova", "Errore")
            window.rollback()
    except Exception as e_standard:
        Alert().fire("Errore durante l'invio.\nControllare il file di log per maggiori dettagli", "Errore")
        Log(e_standard)
        window.rollback()


def send_to_list_in_thread(list_of_numbers, wrong_num, start_idx,  text_list, list_of_photos, window):
    threading.Thread(target=send_to_list,
                     args=(list_of_numbers, wrong_num, start_idx,  text_list, list_of_photos, window),
                     daemon=True).start()


def check_if_open(exename='chrome.exe'):
    for proc in psutil.process_iter(['pid', 'name']):
        # This will check if there exists any process running with executable name
        if proc.info['name'] == exename:
            return True
    return False


def wait_until(driver, x_path_string, disappears=False, exc=constants.except_message_timeout_reached):
    i = constants.TIMEOUT
    if not disappears:
        while i > 0 and len(driver.find_elements(By.XPATH, x_path_string)) == 0:
            time.sleep(1)
            i -= 1
    else:
        while i > 0 and len(driver.find_elements(By.XPATH, x_path_string)) > 0:
            time.sleep(1)
            i -= 1
    if i == 0:
        raise TimeoutException(exc)


def dump_inexistent_numbers(number_list):
    f = open("Numeri inesistenti " + str(datetime.now().date()) + ".txt", mode="a")
    f.write("Indice\t\tNumero di telefono\n")
    for number in number_list:
        f.write(str(number[0]+1) + '\t\t' + str(number[1]) + '\n')
    f.close()


def update_driver():
    chromedriver_autoinstaller.install()
