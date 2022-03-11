from Database import Database
import re
db = Database('dbcfg.ini').connect()


def remove_html_tags(row):
    article_formatted = re.sub('<.*?>', '', row[1])
    db.update_article(row[0], article_formatted)


db.execute_and_run('SELECT * FROM articles WHERE link LIKE %s', ['%icis.com%'],  callback=remove_html_tags, progress_bar=True)
