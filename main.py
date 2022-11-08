import csv
import packaging
from timeit import default_timer as timer
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

JPDB_URL = '''https://jpdb.io/visual-novel-difficulty-list'''

if __name__ == '__main__':
    start = timer()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(JPDB_URL)

    next_page_present = True
    while next_page_present:
        # Gets all the visual novel entries
        entries = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR,
             'body > div.container.bugfix > * > div:nth-child(2) > div:nth-child(3) > div:nth-child(4) > a')))
        # Gets a link to details for every entry
        for entry in entries:
            site_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            link = entry.get_attribute('href')
            print("Getting " + link)
            site_driver.get(link)

            # Title
            try:
                title = WebDriverWait(site_driver, 1).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'body > div.container.bugfix > div:nth-child(2) > div:nth-child(2) > h5')))
                title = title.text
            except TimeoutError:
                print('No title found')
                continue

            # Characters
            try:
                characters = WebDriverWait(site_driver, 1).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'body > div.container.bugfix > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(10) > td')))
                characters = characters.text
            except TimeoutError:
                print('No characters found')
                continue

            # Lines
            try:
                lines = WebDriverWait(site_driver, 1).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'body > div.container.bugfix > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(13) > td')))
                lines = lines.text
            except TimeoutError:
                print('No lines found')
                continue

            # Script size UTF-8
            try:
                script_utf = WebDriverWait(site_driver, 1).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'body > div.container.bugfix > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(15) > td')))
                script_utf = script_utf.text
                script_utf = script_utf[:-2] # deleting the kB unit
            except TimeoutError:
                print('No utf script found')
                continue

            # Script size SJIS
            try:
                script_sjis = WebDriverWait(site_driver, 1).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'body > div.container.bugfix > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(16) > td')))
                script_sjis = script_sjis.text
                script_sjis = script_sjis[:-2] # deleting the kB unit
            except TimeoutError:
                print('No sjis script found')
                continue

            with open('jpdb_vn_stats.csv', 'a', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f,delimiter=';')
                    writer.writerow([title, characters, lines, script_utf, script_sjis])

        # Checking whether there's the next page
        try:
            next_page_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[contains(text(), 'Next page')]")))
            next_page_link = next_page_button.get_attribute('href')
            print("Button clicked")
            driver.get(next_page_link)
        except WebDriverException:
            print("No next page, exiting loop")
            next_page_present = False

    end = timer()
    print(f'Task finished, it took {end - start} seconds to scrape the page.')