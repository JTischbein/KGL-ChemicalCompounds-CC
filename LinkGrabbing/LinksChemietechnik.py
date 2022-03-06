from Database import Database
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_links_from_pages(URL):

    links = []
    page = 1

    # Iterate through all pages
    while True:

        # Get article listing html (example: "https://www.chemietechnik.de/markt.html?page=" + 2 for second page)
        website = requests.get(URL + str(page))

        # Parse HTML with BS
        results = BeautifulSoup(website.content, 'html.parser')

        # Find wrapper div of article listing
        news_wrapper = results.find('div', class_='post-list topicbox')

        # If there are no article links, break
        if news_wrapper is None: break

        # Get date and article html elements
        date_elements = news_wrapper.find_all('div', 'postlist-meta')
        article_elements = news_wrapper.find_all('a', 'postlist-item media d-flex')

        # iterate through articles
        for i in range(len(date_elements)):
            # Get date
            date_span = date_elements[i].find('span', class_='date')
            datetime_object = datetime.strptime(date_span["content"].split("T")[0], '%Y-%m-%d')

            # Get article link
            article = article_elements[i]
            links.append([article["href"], datetime_object])

        # Go to next page
        page += 1

    return links

def run():
    # Get newslistings from file
    with open('ChemietechnikURLs.txt') as f:
        lines = f.readlines()

    urls = [l.replace("\n", "") for l in lines]
    print("URLs:", lines)

    # Connect to database
    db = Database('dbcfg.ini').connect()

    article_links = []

    count = 0

    # Iterate every article listing
    for url in urls:
        # Get all links to article from listing
        article_links = get_links_from_pages(url)

        # Count links
        count += len(article_links)
        
        # Save links in database
        for l in article_links:
            db.add_article(l[0], release_date=l[1])


    print("Found", count, "links and saved them in DB.")
