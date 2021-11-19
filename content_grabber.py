from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from tqdm import tqdm

import psycopg2

import config

conn = psycopg2.connect(host=config.host, port=config.port, dbname=config.dbname, user=config.user, password=config.password)

cur = conn.cursor()
# get all links from chemamager which are actually working
cur.execute("SELECT link FROM articles WHERE link LIKE 'https://www.chemanager-online.com/%' AND release_date IS NOT NULL")
data = cur.fetchall()

CHROMEDRIVER_PATH = config.chrome_driver
s = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service = s)

i = 0
for link in tqdm(data):
    i += 1
    driver.get(link[0])
    # Article library does not work here properly. We have to extract the text from the div manuall
    div = driver.find_element(By.XPATH, "//div[@class='paragraph paragraph--type--text paragraph--view-mode--default']")
    text = div.text
    cur.execute("UPDATE articles SET content = %s WHERE link = %s", (text, link))
    if i % 100 == 0: conn.commit()

conn.commit()
cur.close()
conn.close()

driver.quit()
