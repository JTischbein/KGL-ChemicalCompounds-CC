import sys
import time
sys.path.append('../')

from Database import Database
from urllib.parse import urlparse
from newspaper import Article


def get_content(l, db):
    link = l[0]
    if urlparse(link).netloc != "www.chemietechnik.de":
        return

    done = 0

    while done < 10:
        done += 1
        try:
            article = Article(link)
            article.download()
            article.parse()
            db.update_article(link, content=article.text)
            done = 10
        except Exception as e:
            print(e)
            print("Retry....")
            time.sleep(10)


def run():
    db = Database('../dbcfg.ini').connect()

    if db is None:
        print("DB not connected")
        sys.exit()

    db.execute_and_run("SELECT link FROM articles", attributes=(), callback=lambda l: get_content(l, db), progress_bar=True)

run()
