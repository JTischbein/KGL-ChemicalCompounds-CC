import spacy
from tqdm import tqdm

import countries_dict as countries_dict

import sys
sys.path.append('../')
from Database import Database 

db = Database('../config.ini').connect()

articles = db.execute("SELECT link, content, language FROM articles WHERE content IS NOT NULL")

article_count = 0

english_nlp = spacy.load("en_core_web_sm")
german_nlp = spacy.load("de_core_news_sm")

for article in tqdm(articles):
    article_count += 1

    if article[2] == "en":
        nlp = english_nlp
    else:
        nlp = german_nlp

    doc = nlp(article[1])
    nouns=[chunk.text for chunk in doc.noun_chunks]

    for noun in nouns:
        country = countries_dict.countries_dict.get(noun)
        if country is not None:
            db.execute("INSERT INTO locations (link, synonym, iso) VALUES (%s, %s, %s)", (article[0], noun, country))

