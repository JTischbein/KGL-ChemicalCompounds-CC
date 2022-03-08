import psycopg2
from newspaper import Article

HOST = ""
PORT = ""
DBNAME = ""
USER = ""
PASSWORD = ""
CHANGE_NUMBER_FOR_COMMIT = 10

conn = psycopg2.connect(host=HOST, port=PORT, dbname=DBNAME, user=USER,
                                password=PASSWORD)
cur = conn.cursor()

cur.execute("SELECT DISTINCT link, release_date FROM articles WHERE link LIKE 'https://news.ihsmarkit.com%' AND '2016-12-31' >= release_date")
article_links = cur.fetchall()
article_links = [article_link[0] for article_link in article_links]

def save_in_db(changes):
    for change in changes:
        cur.execute("UPDATE articles SET content = %s WHERE link = %s", (change[0], change[1]))
    conn.commit()

changes = []
for article_link in article_links:
    article = Article(article_link)
    article.download()
    article.parse()
    changes.append((article.text.split("About IHS Markit")[0], article_link))
    if len(changes) == CHANGE_NUMBER_FOR_COMMIT:
        save_in_db(changes)
        changes = []

save_in_db(changes) #for the possibly last CHANGE_NUMBER_FOR_COMMIT - 1 changes

cur.close()
conn.close()