import sys
import spacy
from lodstorage.query import Query
from Database import Database
from lodstorage.sparql import SPARQL
from urllib.parse import urlparse

category = 'chemicals'

substanceQueryStr = """
    SELECT DISTINCT ?substance
    WHERE { 
    VALUES ?substanceLabel {%s}
    ?substance wdt:P31 wd:Q11173;
                rdfs:label|skos:altLabel ?substanceLabel.
    }
    """


endpoint = SPARQL("https://query.wikidata.org/sparql")

db = Database('../dbcfg.ini').connect()

# Load spacy 
nlp_de = spacy.load('de_dep_news_trf')

nlp_en = spacy.load('en_core_web_trf')


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


def query(words, language):
    global substanceQueryStr

    q = substanceQueryStr % (words, language)

    query = Query(query=q,
                  name="Recognized chemical compounds",
                  lang="sparql")
    queryResLoD = endpoint.queryAsListOfDicts(query.query)
    entries = [record.get('entry') for record in queryResLoD]

    return entries


def check_for_any(nouns, language):
    nouns = [noun.replace("\n", " ").strip() for noun in nouns]
    # building the query string
    values = [' '.join([f'"{noun}"@{language}' for noun in nouns[n * 50:n * 50 + 50]]) for n in range((len(nouns) // 50) + 1)]

    return query("\n".join(values), language)


def process_article(line):
    # Get link, text and language
    link = line[0]
    text = line[1]
    language = line[3]

    # If text is empty, skip article
    if text == "" or text is None:
        return

    # Remove "
    text = text.replace('"', '')

    # Load correct model
    if language == "de":
        nlp = nlp_de
    else:
        nlp = nlp_en

    doc = nlp(text)
    nl = "\n"

    try:
        s = check_for_any([chunk.text for chunk in doc.noun_chunks])
        if len(s) == 0:
            return
    except Exception as e:
        save_error(link)
        return

    nouns = [f'"{chunk.text.replace(nl, "").strip()}"@{language}' for chunk in doc.noun_chunks]

    for word in nouns:
        try:
            entries = query(word, language)

            if len(entries) > 0:
                entity_tags = [urlparse(sub).path.split("/")[-1] for sub in entries]
                synonym = word.split('"')[1]
                for tag in entity_tags:
                    db.add_word(category, link, synonym, tag)
                    #print(category, link, synonym, tag)
        except Exception as e:
            print("Unexpected error:", e)
            save_error(link, word, e)
            continue


if db is None:
    print("Connecting to DB failed. Quitting...")
    sys.exit()

db.execute_and_run('SELECT * FROM articles', attributes=(), callback=process_article, progress_bar=True)
