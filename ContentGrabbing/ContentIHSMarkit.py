from newspaper import Article
import sys
sys.path.append('../')
from Database import Database 

db = Database('../config.ini').connect()

CHANGE_NUMBER_FOR_COMMIT = 10


article_links = db.execute("SELECT DISTINCT link, release_date FROM articles WHERE link LIKE 'https://news.ihsmarkit.com%' AND '2016-12-31' >= release_date")

article_links = [article_link[0] for article_link in article_links]

def save_in_db(changes):
    for change in changes:
        db.execute("UPDATE articles SET content = %s WHERE link = %s", (change[0], change[1]))

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
