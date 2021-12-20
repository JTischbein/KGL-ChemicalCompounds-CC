from Database import Database
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_links_from_pages(URL):
    print("Get links from: ", URL)

    links = []
    page = 1

    while True:

        website = requests.get(URL + str(page))
        results = BeautifulSoup(website.content, 'html.parser')

        news_wrapper = results.find('div', class_='post-list topicbox')
        if news_wrapper is None: break

        date_elements = news_wrapper.find_all('div', 'postlist-meta')
        article_elements = news_wrapper.find_all('a', 'postlist-item media d-flex')
        for i in range(len(date_elements)):
            date_span = date_elements[i].find('span', class_='date')

            datetime_object = datetime.strptime(date_span["content"].split("T")[0], '%Y-%m-%d')

            article = article_elements[i]
            links.append([article["href"], datetime_object])

        print(URL, page)

        page += 1

    return links


with open('ChemietechnikURLs.txt') as f:
    lines = f.readlines()

urls = [l.replace("\n", "") for l in lines]
print("URLs:", lines)


db = Database('dbcfg.ini').connect()

article_links = []

count = 0

for url in urls:
    article_links = get_links_from_pages(url)
    count += len(article_links)
    print("Saving in DB")
    for l in article_links:
        db.add_article(l[0], release_date=l[1])


print("Found", count, "links and saved them in DB.")
