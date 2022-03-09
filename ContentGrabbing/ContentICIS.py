from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as ec

import sys
sys.path.append('../')
from Database import Database 

config = ConfigParser()
config.read("../config.ini")

PROFILE = config["SELENIUM"]["DRIVERTIM"]


class ICIS_content:

    def __init__(self):
        options = Options()
        options.headless = True
        options.profile = webdriver.FirefoxProfile(
            PROFILE)
        self.driver = webdriver.Firefox(options=options)
        get_content(self)
        self.driver.quit()

    global new_website, get_content, save_in_db

    def new_website(self, url):
        try:
            self.driver.get(url)
        except:
            print(url + " can't be reached. Shutting down...")
            self.driver.quit()

    def get_content(self):
        i = 0
        url_base = "https://www.icis.com/explore/wp-admin/admin-ajax.php?action=article-search-data&pub_date=&geo=&article_type=&current_page="
        while True:
            try:
                i += 1
                print(i)
                url = url_base + str(i)
                new_website(self, url)

                content = wait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//span[@class="objectBox objectBox-string"]')))

                if content.text == '""': break

            except:
                continue
            save_in_db([url, "".join("".join(content.text.replace("  ", "").split("\\n")).split("\\t"))])

    def save_in_db(content):
        db = Database('../config.ini').connect()

        print(content)
        db.execute("INSERT INTO articles (link, content) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (content[0], content[1]))


ICIS_content()