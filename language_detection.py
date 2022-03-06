import psycopg2
import langid
from tqdm import tqdm

import config

conn = psycopg2.connect(host=config.host, port=config.port, dbname=config.dbname, user=config.user, password=config.password)
cur = conn.cursor()

cur.execute("ALTER TABLE articles ADD language CHAR(2)")

cur.execute("SELECT link, content FROM articles")
articles = cur.fetchall()

for article in tqdm(articles):
    language = langid.classify(article[1])[0]
    cur.execute("UPDATE articles SET language = %s WHERE link = %s", (language, article[0]))

conn.commit()

cur.close()
conn.close()