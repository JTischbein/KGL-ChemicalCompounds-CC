# This Script crawls in all articles for companies by quering them with the below wikidata sparql query

import sys
sys.path.append('../')
import spacy
from Database import Database
from lodstorage.sparql import SPARQL
from lodstorage.query import Query


endpoint = SPARQL("https://query.wikidata.org/sparql")

db = Database('../config.ini').connect()


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


def query_db(word):
    return db.execute('SELECT * FROM company_dict WHERE position(name in %s) > 0;', attributes=(word,), fetch=True)

def query_wd(word):
    q = """
        SELECT ?company ?companyLabel (group_concat(?instanceOfLabel;separator=',') as ?instanceOfLabels)
        WHERE 
        {
        VALUES ?companyLabel { "%s"@en }
        ?company wdt:P452 wd:Q207652.  
        ?company rdfs:label ?companyLabel filter (lang(?companyLabel) = "en"). 
        ?company wdt:P31 ?instanceOf.
        ?instanceOf rdfs:label ?instanceOfLabel filter (lang(?instanceOfLabel) = "en"). 
        } 
        GROUP BY ?company ?companyLabel
        ORDER BY ?companyLabel
    """

    q = q % (word)

    query = Query(query=q,
                  name="Company",
                  lang="sparql")
    queryResLoD = endpoint.queryAsListOfDicts(query.query)
    entries = [record.get('entry') for record in queryResLoD]

    return entries


def process_article(line):
    link = line[0]
    text = line[1]
    language = line[3]
    if text == "" or text is None:
        return

    if language == "de":
        nlp = spacy.load('de_dep_news_trf')
    else:
        nlp = spacy.load('en_core_web_trf')

    text = text.replace('"', '')

    doc = nlp(text)
    nl = "\n"

    try:
        #s = check_for_any([chunk.text for chunk in doc.noun_chunks])
        #if len(s) == 0:
        #    return
        print(link)
    except Exception as e:
        print("Unexpected error:", str(e))
        save_error(link, error=str(e))
        return

    nouns = [chunk.text for chunk in doc.noun_chunks]
    #print(nouns)
    #return

    for word in nouns:
        try:
            print(query_db(word))

        except Exception as e:
            print("Unexpected error:", e)
            save_error(link, word, str(e))


if db is None:
    print("Connecting to DB failed. Quitting...")
    sys.exit()

db.execute_and_run('SELECT * FROM articles LIMIT 10;', attributes=(), callback=process_article, progress_bar=True)
