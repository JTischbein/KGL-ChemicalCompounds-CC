import sys
sys.path.append('../')
from Database import Database
import requests
from bs4 import BeautifulSoup
from datetime import datetime


website = requests.get("https://en.wikipedia.org/wiki/List_of_largest_chemical_producers")
results = BeautifulSoup(website.content, 'html.parser')

#print(results.prettify())
table = results.find('tbody', class_='')

#print(table)

rows = table.find_all('tr')

companies = []

for row in rows:
    title = row.find_all('a')[0].get('title')
    if title != None:
        companies.append(title)

print(companies)
print(len(companies))

db = Database('./config.ini').connect()

for word in companies:
    db.add_word_to_dict('company_dict', word)

