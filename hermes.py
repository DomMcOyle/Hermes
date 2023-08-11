from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW

from datetime import datetime
import time
import os.path
import threading


import psutil
import chromedriver_autoinstaller

import constants
from alert import TimeoutException
from debug import Log



def initialize_web_driver():
    print(1)
    homedir = os.path.expanduser("~")

    op = Options()
    op.add_argument("--user-data-dir=" + homedir + "\\AppData\\Local\\Google\\Chrome\\User Data")
    op.add_experimental_option("excludeSwitches", ["enable-automation"])
    op.add_experimental_option("useAutomationExtension", False)
    #op.add_argument("--silent")
    print(2)
    service = Service("chromedriver.exe")
    service.creationflags = CREATE_NO_WINDOW
    print(3)
    driver = webdriver.Chrome(service=service,
                              options=op)
    print(4)
    driver.maximize_window()
    return homedir, op, driver


def wa_send(driver, string_of_photos):

    if string_of_photos:
        wait_until(driver, ["//span[@data-icon='attach-menu-plus']"])
        driver.find_element(By.XPATH, "//span[@data-icon='attach-menu-plus']").click()
        inv = driver.find_element(By.XPATH, "//input[@type='file']")
        inv.send_keys(string_of_photos)
    wait_until(driver, ["//span[@data-icon='send']"])
    time.sleep(1)
    driver.find_element(By.XPATH, "//span[@data-icon='send']").click()
    time.sleep(1)
    wait_until(driver, ["//span[@data-icon='msg-time']"], disappears=True)


def send_to_list(list_of_numbers, wrong_num_idx, start_idx,  text_list, list_of_photos, window):
    i = start_idx
    num_wrong = 0
    n_retries = 0
    timeout = False
    print('mandando')
    try:
        print('inizializzazione web driver')
        homedir, op, driver = initialize_web_driver()
        # controllo d'accesso (non mi viene un'idea migliore)
        print('aprendo whatsapp')
        driver.get("https://web.whatsapp.com")  # apri whatsapp
        print('capiamo')
        wait_until(driver, ["//div[@aria-label='Scan me!']"], disappears=True, exc=constants.except_message_qr)
        wait_until(driver, ["//div[@id='side']"])
        inexistent_numbers = []

        string_of_photos = ""
        if len(list_of_photos) > 0:
            string_of_photos = list_of_photos[0]
            for photo in range(1, len(list_of_photos)):
                string_of_photos += ('\n' + list_of_photos[photo])
        total_rows = len(list_of_numbers) + len(wrong_num_idx)

        print(start_idx)
        print(total_rows)
        print(wrong_num_idx)
        while i < total_rows:
            # Blocco per la gestione della pausa
            if window.get_kill_thread_value():
                window.rollback(i)
                return
            while window.get_pause_thread_value():
                if window.get_kill_thread_value():
                    window.rollback(i)
                    return
                time.sleep(1)
            # blocco per l'invio dell'iesimo messaggio
            try:
                if i not in wrong_num_idx:
                    driver.get("https://web.whatsapp.com/send?phone=" + list_of_numbers[i-num_wrong] + "&text=" + text_list) #lancia
                    time.sleep(1)
                    appeared_index = wait_until(driver, ["//*[contains(text(), 'via url non valido')]",
                                                         "//span[@data-icon='search-alt']"])
                    # indice di queli dei due nella lista precedente è apparso
                    if appeared_index == 0:
                        inexistent_numbers.append([i, list_of_numbers[i-num_wrong]])

                    else:
                        wa_send(driver, string_of_photos)
                else:
                    inexistent_numbers.append([i, "Numero incorretto."])
                    num_wrong = wrong_num_idx.index(i) + 1

            # blocco per il retry di un invio
            except TimeoutException as te:
                if n_retries < constants.NUM_RETRIES:
                    print("riprovo")
                    print(i)
                    n_retries = n_retries + 1
                    timeout = True
                else:
                    raise te

            # update progress bar e indice
            if not timeout:
                window.update_progress_bar()
                n_retries = 0
                i = i + 1
            else:
                timeout = False


        driver.close()
        not_found_warning = False
        if len(inexistent_numbers) > 0:
            not_found_warning = True
            dump_inexistent_numbers(inexistent_numbers)

        window.finalize_send(not_found_warning)
    except WebDriverException as e:
        if e.msg == "chrome not reachable":
            window.fire_alert("Chrome non raggiungibile.\nSe è stato chiuso premere nuovamente \"Invia\"", "Errore")
            window.rollback(i)
        else:
            Log(e)
            window.fire_alert("Errore durante l'invio.\nControllare il file di log per maggiori dettagli", "Errore")
            window.rollback(i)
    except NoSuchWindowException:
            window.fire_alert("Chrome non raggiungibile.\nSe è stato chiuso premere nuovamente \"Invia\"", "Errore")
            window.rollback(i)
    except TimeoutException as te:
        if te.msg == constants.except_message_timeout_reached:
            window.fire_alert("Errore durante l'invio, controlla la connessione di rete e riprova", "Errore")
            window.rollback(i)
        elif te.msg == constants.except_message_qr:
            window.fire_alert("Tempo per l'autenticazione (QR code) scaduto, esegui l'accesso e riprova", "Errore")
            window.rollback()
    except Exception as e_standard:
        Log(e_standard)
        window.fire_alert("Errore durante l'invio.\nControllare il file di log per maggiori dettagli", "Errore")
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


def wait_until(driver, x_path_string_list, disappears=False, exc=constants.except_message_timeout_reached):
    # attende che compaia uno degli elementi della lista o non appena uno degli elementi scompare
    # restituisce l'indice dell'elemento che è comparso/scomparsa
    i = constants.TIMEOUT
    if not disappears:
        while i > 0:
            for j in range(len(x_path_string_list)):
                if len(driver.find_elements(By.XPATH, x_path_string_list[j])) > 0:
                    return j
            time.sleep(1)
            i -= 1
    else:
        while i > 0:
            for j in range(len(x_path_string_list)):
                if len(driver.find_elements(By.XPATH, x_path_string_list[j])) == 0:
                    return j
            time.sleep(1)
            i -= 1
    if i == 0:
        raise TimeoutException(exc)


def dump_inexistent_numbers(number_list):
    f = open(constants.log_path + "Numeri inesistenti " + str(datetime.now().date()) + ".txt", mode="a")
    f.write("Indice\t\t\t\tNumero di telefono\n")
    for number in number_list:
        f.write(str(number[0]+1) + '\t\t\t\t' + str(number[1]) + '\n')
    f.close()


def update_driver():
    chromedriver_autoinstaller.install()
