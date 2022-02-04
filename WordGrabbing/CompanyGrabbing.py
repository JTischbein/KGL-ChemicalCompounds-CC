import sys
sys.path.append('../')
import spacy
from Database import Database
from urllib.parse import urlparse

category = 'companies'

db = Database('../dbcfg.ini').connect()

if db is None:
    print("Connecting to DB failed. Quitting...")
    sys.exit()

company_names = [name[0] for name in db.execute('SELECT name FROM company_wikidata')]


nlp_de = spacy.load('de_dep_news_trf')

nlp_en = spacy.load('en_core_web_trf')

all_insertions = []


def save_error(link, word="", error=""):
    f = open("errorlinks.txt", "a")
    f.write("--------------------------\n")
    if word == "":
        f.write(link)
    else:
        f.write(word + " " + link)
    f.write("\n")
    if error != "":
        f.write(error)
        f.write("\n")
    f.write("--------------------------\n")
    f.close()


def query(word):
    entries = db.execute('SELECT word FROM company_dict WHERE name=', attributes=(word,))

    entries = [x[0] for x in entries]

    return entries


def check_for_any(text):
    res = []
    for comp in company_names:
        if comp in text:
            res.append(comp)

    return res


def process_article(line):

    # Get data and check if text existing
    link = line[0]
    text = line[1]
    language = line[3]
    if text == "" or text is None:
        print("None")
        return

    # Remove all "
    text = text.replace('"', '')

    # Set NLP language
    if language == "de":
        nlp = nlp_de
    else:
        nlp = nlp_en

    # Process Text
    doc = nlp(text)
    all_nouns = [chunk.text for chunk in doc.noun_chunks]

    # Check if there is any Company in the text
    try:
        upcoming_names = check_for_any(text)
        if len(upcoming_names) == 0:
            return
    except Exception as e:
        # Save error message for debugging
        save_error(link, error=str(e))
        return
    
    for comp in upcoming_names:
        all_insertions.append((link, comp))

    

db.execute_and_run('SELECT * FROM articles', attributes=(), callback=process_article, progress_bar=True)

print(len(all_insertions))