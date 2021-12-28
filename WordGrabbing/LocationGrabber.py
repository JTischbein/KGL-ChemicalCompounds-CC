import spacy
from geotext import GeoText
import psycopg2
from tqdm import tqdm

import config
import countries_dict

conn = psycopg2.connect(host=config.host, port=config.port, dbname=config.dbname, user=config.user, password=config.password)

cur = conn.cursor()

cur.execute("SELECT link, content, language FROM articles WHERE content IS NOT NULL")
articles = cur.fetchall()

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
            cur.execute("INSERT INTO locations (link, synonym, iso) VALUES (%s, %s, %s)", (article[0], noun, country))
            if article_count % 500 == 0:
                conn.commit()

conn.commit()

cur.close()
conn.close()
