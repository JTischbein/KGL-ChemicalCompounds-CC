from Database import Database
from langdetect import detect_langs, DetectorFactory, detect

#DetectorFactory.seed = 0

db = Database('../dbcfg.ini').connect()


def set_lang_for_article(line):
    if not line[1] or line[1] == "": return
    lang = detect(line[1])
    print(lang)
    db.set_language(line[0], lang)


db.execute_and_run('SELECT * FROM articles', callback=set_lang_for_article, progress_bar=True)
