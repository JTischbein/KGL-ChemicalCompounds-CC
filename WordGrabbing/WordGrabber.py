import sys
import spacy
from lodstorage.query import Query
from Database import Database
from lodstorage.sparql import SPARQL
from urllib.parse import urlparse

endpoint = SPARQL("https://query.wikidata.org/sparql")

db = Database('./dbcfg.ini').connect()



def save_error(link, word=""):
    f = open("errorlinks.txt", "a")
    if word == "":
        f.write(link)
    else:
        f.write(word + " " + link)
    f.write("\n")
    f.close()

def query(words):
    substanceQueryStr = """
    SELECT DISTINCT ?entry ?entry2
    WHERE { 
      VALUES ?entryLabel {%s}
      {?entry wdt:P31 wd:Q83405.} UNION
      {?sup wdt:P279 wd:Q83405.
      ?entry wdt:P31 ?sup.}
      ?entry rdfs:label|skos:altLabel ?entryLabel.
      OPTIONAL {?entry wdt:P1542 ?entry2.
      ?entry2 wdt:P31 wd:Q58734.}
      FILTER(lang(?entryLabel) = "en").
    }
    """

    q = substanceQueryStr % words
    query = Query(query=q,
                            name="Recognized chemical compounds",
                            lang="sparql")
    queryResLoD = endpoint.queryAsListOfDicts(query.query)
    entries = [record.get('entry') for record in queryResLoD]

    return entries

def check_for_any(nouns):
    nouns = [noun.replace("\n", " ").strip() for noun in nouns]
    # building the query string
    values = [' '.join([f'"{noun}"@en' for noun in nouns[n * 50:n * 50 + 50]]) for n in range((len(nouns) // 50) + 1)]
    
    return query("\n".join(values))


# TODO: Sprache berücksichtigen

def process_article(line):
    link = line[0]
    text = line[1]
    if text == "" or text is None:
        return

    text = text.replace('"', '')

    # NLP on text
    nlp = spacy.load('de_core_news_sm')
    doc = nlp(text)
    nl = "\n"

    try:
        s = check_for_any([chunk.text for chunk in doc.noun_chunks])
        if len(s) == 0:
            return
    except Exception as e:
        save_error(link)

    nouns = [f'"{chunk.text.replace(nl, "").strip()}"@en' for chunk in doc.noun_chunks]

    
    
    for word in nouns:
        try:
            entries = query(word)

            if len(entries) > 0:
                x = [urlparse(sub).path.split("/") for sub in entries]
                entity_tags = [sub[len(sub) - 1] for sub in x]
                synonym = word.split('"')[1]
                for tag in entity_tags:
                    db.add_word('companies', link, synonym, tag)
        except Exception as e:
            #print("Unexpected error:", e)
            continue


if db is None:
    print("Connecting to DB failed. Quitting...")
    sys.exit()

db.execute_and_run('SELECT link, content FROM articles', attributes=(),
                   callback=lambda l: process_article(l))

