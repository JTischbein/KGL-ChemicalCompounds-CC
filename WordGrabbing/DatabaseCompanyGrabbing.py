import sys
sys.path.append('../')
import spacy
from Database import Database
from urllib.parse import urlparse

# Connect to DB
db = Database('../config.ini').connect()

if db is None:
    print("Connecting to DB failed. Quitting...")
    sys.exit()

# Get all company names
company_names = [line[0] for line in db.execute('SELECT name FROM companies_wikidata')]


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


def check_for_any(text):
    res = []
    for comp in company_names:
        if comp in text:
            res.append(comp)

    return res


def process_article(line):
    # Get data and check if text exists
    link = line[0]
    text = line[1]

    if text == "" or text is None:
        return

    # Remove all "
    text = text.replace('"', '')

    # Check if there is any Company in the text
    try:
        upcoming_names = check_for_any(text)
        if len(upcoming_names) == 0:
            return
    except Exception as e:
        # Save error message for debugging
        save_error(link, error=str(e))
        print(link, str(e))
        return
    
    for comp in upcoming_names:
        db.execute('INSERT INTO companies (link, synonym) VALUES (%s, %s)', attributes=(link, comp))

    
# Run process_article for every article
db.execute_and_run('SELECT * FROM articles', attributes=(), callback=process_article, progress_bar=True)
