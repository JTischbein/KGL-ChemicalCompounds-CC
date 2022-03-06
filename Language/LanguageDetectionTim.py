import psycopg2
import fasttext

fasttext.FastText.eprint = lambda x: None

PRETRAINED_MODEL_PATH = ''
CHANGE_NUMBER_FOR_COMMIT = 300

HOST = ""
PORT = ""
DBNAME = ""
USER = ""
PASSWORD = ""

conn = psycopg2.connect(host=HOST, port=PORT, dbname=DBNAME, user=USER,
                                password=PASSWORD)
cur = conn.cursor()

cur.execute("SELECT DISTINCT content, language, link FROM articles WHERE link LIKE '%markit.com%'")
articles = cur.fetchall()

def save_in_db(changes):
    for change in changes:
        cur.execute("UPDATE articles SET language = %s WHERE link = %s", (change[0], change[1]))
    conn.commit()

model = fasttext.load_model(PRETRAINED_MODEL_PATH)

changes = []

for article in articles:
    try:
        language = model.predict(article[0].replace("\n", ""))[0][0].split("__label__")[1]
        if language != article[1]:
            changes.append((language, article[2]))
        if len(changes) == CHANGE_NUMBER_FOR_COMMIT:
            save_in_db(changes)
            changes = []
    except:
        continue

save_in_db(changes) #for the possibly last CHANGE_NUMBER_FOR_COMMIT - 1 changes

cur.close()
conn.close()