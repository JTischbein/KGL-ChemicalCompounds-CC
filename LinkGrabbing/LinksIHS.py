from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from datetime import date, datetime
import calendar
import sys
sys.path.append('../')
from Database import Database 



HOST = ""
PORT = ""
DBNAME = ""
USER = ""
PASSWORD = ""
PROFILE = ""


class URL_list:

    def __init__(self):
        options = Options()
        options.headless = True
        options.profile = webdriver.FirefoxProfile(PROFILE)
        self.driver = webdriver.Firefox(options=options)
        get_links(self)
        self.driver.quit()

    global new_website, get_links, save_in_db

    def new_website(self, url):
        try:
            self.driver.get(url)
        except:
            print(url + " can't be reached. Shutting down...")
            self.driver.quit()

    def get_links(self):
        new_website(self, "https://news.ihsmarkit.com/INFO/press_releases")
        self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="iframe_press"]'))
        year = date.today().year
        number_years = 5
        links = []

        while number_years != 0:
            self.driver.find_element_by_link_text(str(year - number_years + 1)).click()  # year button
            number_years -= 1
            last_page = False

            while not last_page:
                news_urls = self.driver.find_elements_by_xpath("//span[@class='field-content title']/a")
                news_dates = self.driver.find_elements_by_xpath("//div[@class='field-content teaser']/p")
                for i in range(len(news_dates)):
                    date_parts = news_dates[i].text.split(", ")[1:4]
                    date_parts[0] = list(calendar.month_name).index(date_parts[0])
                    datetime_object = datetime(int(date_parts[2]),date_parts[0],int(date_parts[1]))

                    links.append([news_urls[i].get_attribute("href"), datetime_object])
                try:
                    self.driver.find_element_by_xpath("//li[@class='next page']/a[@class='type_link']").click()  # next button
                except NoSuchElementException:
                    last_page = True

        save_in_db(links)

    def save_in_db(links):
        db = Database('../dbcfg.ini').connect()

        for link in links:
            print(link)
            db.execute("INSERT INTO articles (link, release_date) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (link[0], link[1]))


URL_list()
