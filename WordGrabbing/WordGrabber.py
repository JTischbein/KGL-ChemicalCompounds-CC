import sys
import spacy
from lodstorage.query import Query
from Database import Database
from lodstorage.sparql import SPARQL
from urllib.parse import urlparse

endpoint = SPARQL("https://query.wikidata.org/sparql")

db = Database('./dbcfg.ini').connect()


# Print iterations progress (stolen from stack overflow)
def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print(f'\r', end = printEnd)


def save_error(link, word=""):
    f = open("errorlinks.txt", "a")
    if word == "":
        f.write(link)
    else:
        f.write(word + " " + link)
    f.write("\n")
    f.close()

def test_josha(x, y):
    for i in range(x):
        y += x
        print("penis")
    return y


def check_for_substances(nouns):
    nouns = [noun.replace("\n", " ").strip() for noun in nouns]
    # building the query string
    values = [' '.join([f'"{noun}"@en' for noun in nouns[n * 50:n * 50 + 50]]) for n in range((len(nouns) // 50) + 1)]
    queryValueFormatTags = '%s\n' * (len(values))
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
    substanceQueryStr = substanceQueryStr % ("\n".join(values))
    # executing the query
    substanceQuery = Query(query=substanceQueryStr,
                           name="Companies",
                           lang="sparql")
    substanceQueryResLoD = endpoint.queryAsListOfDicts(substanceQuery.query)


    substances = [record.get('entry') for record in substanceQueryResLoD]
    return substances




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
        s = check_for_substances([chunk.text for chunk in doc.noun_chunks])
        if len(s) == 0:
            return
    except Exception as e:
        save_error(link)

    nouns = [f'"{chunk.text.replace(nl, "").strip()}"@en' for chunk in doc.noun_chunks]

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
    print()
    for word in progressBar(nouns, prefix = 'Progress:', suffix = 'Complete', length = 50):
        try:
            q = substanceQueryStr % word
            query = Query(query=q,
                                   name="Recognized chemical compounds",
                                   lang="sparql")
            queryResLoD = endpoint.queryAsListOfDicts(query.query)
            entries = [record.get('entry') for record in queryResLoD]

            if len(entries) > 0:
                x = [urlparse(sub).path.split("/") for sub in entries]
                entity_tags = [sub[len(sub) - 1] for sub in x]
                synonym = word.split('"')[1]
                for tag in entity_tags:
                    db.add_word('companies', link, synonym, tag)
        except Exception as e:
            #print("Unexpected error:", e)
            continue
    print("\033[1A\033[1A")


if db is None:
    print("Connecting to DB failed. Quitting...")
    sys.exit()

db.execute_and_run('SELECT link, content FROM articles', attributes=(),
                   callback=lambda l: process_article(l))

