# In some icis articles we have html remains. To remove this, run this script

from Database import Database
import re
db = Database('config.ini').connect()


def remove_html_tags(row):
    article_formatted = re.sub('<.*?>', '', row[1])
    db.update_article(row[0], article_formatted)


db.execute_and_run('SELECT * FROM articles WHERE link LIKE %s', ['%icis.com%'],  callback=remove_html_tags, progress_bar=True)
