import spacy
import nltk
nltk.download("punkt")
from nltk import tokenize
import psycopg2
from tqdm import tqdm
from configparser import ConfigParser

import library

config = ConfigParser()
config.read("../config.ini")
HOST = config["POSTGRES"]["HOST"]
PORT = config["POSTGRES"]["PORT"]
DBNAME = config["POSTGRES"]["DBNAME"]
USER = config["POSTGRES"]["USER"]
PW = config["POSTGRES"]["PASSWORD"]

conn = psycopg2.connect(host=HOST, port=PORT, dbname=DBNAME, user=USER, password=PW)
cur = conn.cursor()          

# We need the content of all articles that were mentioned in the chemical table
cur.execute("SELECT DISTINCT a.content, a.link, a.language FROM articles a, chemicals c WHERE a.link = c.link")
articles = cur.fetchall()
# Firstly, we have to store a list of all chemicals that were mentioned in the articles
cur.execute("SELECT DISTINCT synonym FROM chemicals")
chemicals = cur.fetchall()
chemicals = [chemical[0] for chemical in chemicals]
# Here we have to store the recognized locations
cur.execute("SELECT DISTINCT synonym FROM locations")                                            
locations = cur.fetchall()
locations = [location[0] for location in locations]



cur.execute("SELECT ch.chemical_formula, ch.tag, array_agg(DISTINCT ch2.synonym) FROM chemicals ch LEFT JOIN chemicals ch2 ON ch.chemical_formula = ch2.chemical_formula GROUP BY ch.chemical_formula, ch.tag")
chemical_table = cur.fetchall()
chemical_formulas = [formula[0] for formula in chemical_table]
chemical_synonyms = [synonym[2] for synonym in chemical_table]
chemical_dictionary = {}
for synonyms, formula in zip(chemical_synonyms, chemical_formulas):
    for synonym in synonyms:
        chemical_dictionary[synonym] = formula

for article_count, article in enumerate(tqdm(articles)):
    article_count += 1

    if article[2] == "en":
        nlp = library.english_nlp
        deps = library.english_deps
    else:
        nlp = library.german_nlp
        deps = library.german_deps

    sentences = tokenize.sent_tokenize(article[0])
    noun_sentences = library.get_nouns(sentences)

    article_chemicals, article_locations = library.get_entities(noun_sentences)

    chemical_indices = [chemical[1] for chemical in article_chemicals]
    article_compounds = [chemical[0] for chemical in article_chemicals]
    location_indices = [location[1] for location in article_locations]
    article_countries = [location[0] for location in article_locations]

    for chemical in article_chemicals:
        sentence_index = chemical[1]

        if sentence_index in location_indices:
            sentence = sentences[sentence_index]
            class_1 = False
            for token in nlp(sentence):
                # class 1: location is object of chemical or vice versa
                if token.dep_ in deps and token.text in article_countries:
                    cur.execute("INSERT INTO chemical_location_relations (company, location, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s,  %s)", (chemical[0], token.text, 1, 0, article[1]))
                    class_1 = True
            # class 2: no specific relationship, but appear in the same sentence
            if not class_1:
                cur.execute("INSERT INTO chemical_location_relations (company, location, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (chemical[0], library.get_location(article_locations, sentence_index), 2, 0, article[1]))
            library.remove_location(article_locations, sentence_index)
        article_chemicals.remove(chemical)
    library.closest_entity(article_chemicals, article_locations)

    if article_count % 300 == 0:
        conn.commit()

conn.commit()

cur.close()
conn.close()
