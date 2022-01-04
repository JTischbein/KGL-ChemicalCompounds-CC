from Database import Database
from langdetect import detect_langs, DetectorFactory, detect

#DetectorFactory.seed = 0

db = Database('../dbcfg.ini').connect()

def detect_language(text):
    langs = detect_langs(text)
    for l in langs:
        return l.lang

def detect(line):
    if not line[1] or line[1] == "": return
    lang = detect_language(line[1])
    db.set_language(line[0], lang)


db.execute_and_run('SELECT * FROM articles', callback=detect, progress_bar=True)
