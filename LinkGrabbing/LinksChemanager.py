from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from tqdm import tqdm
from datetime import datetime
import sys
sys.path.append('../')
from Database import Database 

import config

# get all article links of a single news page
def get_links(elements):
    links = []
    for element in elements:
        links.append(element.get_attribute("href"))
    return links

# There are not any datetime elements in the html page. So we have to find them maually
# The date is stored as a text element either in the subtitle or in the teaser-text paragraph
# Some articles encounters unexpected errors when calling. So here we have to return None.
def get_datetime():
    try:
        date = driver.find_element(By.CLASS_NAME, 'subtitle').text.split()[0].replace('.', '-')
        date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        return date
    except (ValueError, IndexError):
        date = driver.find_element(By.CLASS_NAME, 'teaser-text').text.split()[0].replace('.', '-')
        date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        return date
    except Exception:
        return None
    

# function for saving our webcrawled results in a postgresql database
def save_in_db(entries):
    db = Database('../dbcfg.ini').connect()

    for entry in entries:
        db.execute("INSERT INTO articles (link, release_date) VALUES (%s, %s) ON CONFLICT DO NOTHING", (entry[0], entry[1]))


CHROMEDRIVER_PATH = config.chrome_driver
s = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service = s)


entries = []

# iterate over all news pages for the last five years (approx. 683 news pages)
for i in tqdm(range(683)):
    driver.get("https://www.chemanager-online.com/news/news?page="+str(i))
    elements = driver.find_elements(By.CSS_SELECTOR, "div.col-inner.col-inner-3.teaser-image a")
    links = get_links(elements)
    for link in links:
        driver.get(link)
        date = get_datetime()
        entries.append([link, date])


save_in_db(entries)

driver.quit()
