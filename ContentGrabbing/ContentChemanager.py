# Crawling for content of articles from chemanager

from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from tqdm import tqdm

import sys
sys.path.append('../')
from Database import Database 

db = Database('../config.ini').connect()


# get all links from chemamager which are actually working
data = db.execute("SELECT link FROM articles WHERE link LIKE 'https://www.chemanager-online.com/%' AND release_date IS NOT NULL")

config = ConfigParser()
config.read("../config.ini")

CHROMEDRIVER_PATH = config["SELENIUM"]["DRIVERTHEYS"]

s = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service = s)

i = 0
for link in tqdm(data):
    i += 1
    driver.get(link[0])
    # Article library does not work here properly. We have to extract the text from the div manuall
    div = driver.find_element(By.XPATH, "//div[@class='paragraph paragraph--type--text paragraph--view-mode--default']")
    text = div.text
    db.execute("UPDATE articles SET content = %s WHERE link = %s", (text, link))


driver.quit()
