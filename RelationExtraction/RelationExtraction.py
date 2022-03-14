import spacy
import nltk
nltk.download("punkt")
from nltk import tokenize
import psycopg2
from tqdm import tqdm
from configparser import ConfigParser


config = ConfigParser()
config.read("../config.ini")
HOST = config["POSTGRES"]["HOST"]
PORT = config["POSTGRES"]["PORT"]
DBNAME = config["POSTGRES"]["DBNAME"]
USER = config["POSTGRES"]["USER"]
PW = config["POSTGRES"]["PASSWORD"]

conn = psycopg2.connect(host=HOST, port=PORT, dbname=DBNAME, user=USER, password=PW)
cur = conn.cursor()                                                                                                                                                   

# We need the content of all articles that were mentioned in the companies table
cur.execute("SELECT DISTINCT a.content, a.link, a.language FROM articles a, companies c WHERE a.link = c.link")                          
articles = cur.fetchall()
# Firstly, we have to store a list of all companies that were mentioned in the articles
cur.execute("SELECT DISTINCT synonym FROM companies")
companies = cur.fetchall()
companies = [company[0] for company in companies]
# We need a list of all chemicals we've discovered so far 
# so that we can amtch them with the companies
cur.execute("SELECT DISTINCT synonym FROM chemicals")
chemicals = cur.fetchall()
chemicals = [chemical[0] for chemical in chemicals]
# Here wwe have to store the recognized locations
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

# creates a noun list for each sentence
def get_nouns(sentences):
    nouns = []
    for sentence in sentences:
        doc = nlp(sentence)
        nouns.append([chunk.text for chunk in doc.noun_chunks])
    return nouns 

# Allows us to fetch all companies, chemicals and locations from the article
def get_entities(noun_sentences):
    company_list = []
    chemical_list = []
    location_list = []
    for idx, sentence in enumerate(noun_sentences):
        for noun in sentence:
            if noun in companies:
                company_list.append((noun, idx))
            elif noun in chemicals:
                chemical_list.append((noun, idx))
            elif noun in locations:
                location_list.append((noun, idx))
    return company_list, chemical_list, location_list 

def get_chemical(article_chemicals, sentence_index):
    for chemical in article_chemicals:
        if chemical[1] == sentence_index:
            return chemical[0]

def remove_chemical(article_chemicals, sentence_index):
    for chemical in article_chemicals:
        if chemical[1] == sentence_index:
            article_chemicals.remove(chemical)

def get_location(article_locations, sentence_index):
    for location in article_locations:
        if location[1] == sentence_index:
            return location[0]

def remove_location(article_locations, sentence_index):
    for location in article_locations:
        if location[1] == sentence_index:
            article_locations.remove(location)

# For the entities which are left over, we would like to calculate the distance between the entity (chemical or location) and the company
def closest_entity(article_companies, article_chemicals, article_locations):
    # First we have to find the closest chemical to the company
    for company in article_companies:
        if not article_chemicals:
            break
        closest_chemical = article_chemicals[0]
        chemical_distance = abs(company[1] - closest_chemical[1])
        for chemical in article_chemicals:
            if abs(company[1] - chemical[1]) < chemical_distance:
                closest_chemical = chemical
                chemical_distance = abs(company[1] - chemical[1])
        cur.execute("INSERT INTO company_chemical (company, chemical, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (company[0], chemical_dictionary[closest_chemical[0]], 3, chemical_distance, article[1]))
        article_chemicals.remove(closest_chemical)
    # Then we have to find the closest location to the company
    for company in article_companies:
        if not article_locations:
            break
        closest_location = article_locations[0]
        location_distance = abs(company[1] - closest_location[1])
        for location in article_locations:
            if abs(company[1] - location[1]) < location_distance:
                closest_location = location
                location_distance = abs(company[1] - location[1])
        cur.execute("INSERT INTO company_location (company, location, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (company[0], closest_location[0], 3, location_distance, article[1]))
        article_locations.remove(closest_location)


english_deps = ["nsubj", "nsubj_pass", "dobj", "iobj", "pobj"]
german_deps = ["sb", "sbp", "oa", "og", "op"]

english_nlp = spacy.load("en_core_web_trf")
german_nlp = spacy.load("de_dep_news_trf")

for article_count, article in enumerate(tqdm(articles)):
    article_count += 1

    if article[2] == "en":
        nlp = english_nlp
        deps = english_deps
    else:
        nlp = german_nlp
        deps = german_deps

    sentences = tokenize.sent_tokenize(article[0])
    noun_sentences = get_nouns(sentences)

    article_companies, article_chemicals, article_locations = get_entities(noun_sentences)

    chemical_indices = [chemical[1] for chemical in article_chemicals]
    article_compounds = [chemical[0] for chemical in article_chemicals]
    location_indices = [location[1] for location in article_locations]
    article_countries = [location[0] for location in article_locations]

    for company in article_companies:
        sentence_index = company[1]
        if sentence_index in chemical_indices:
            sentence = sentences[sentence_index]
            class_1 = False
            for token in nlp(sentence):
                # class 1: chemical is object of company or vice versa
                if token.dep_ in deps and token.text in article_compounds:
                    cur.execute("INSERT INTO company_chemical (company, chemical, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (company[0], chemical_dictionary[token.text], 1, 0, article[1]))
                    class_1 = True
            # class 2: no specific relationship, but appear in the same sentence
            if not class_1:
                cur.execute("INSERT INTO company_chemical (company, chemical, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (company[0], chemical_dictionary[get_chemical(article_chemicals)], sentence_index), 2,  0,  article[1])
            remove_chemical(article_chemicals, sentence_index)

        if sentence_index in location_indices:
            sentence = sentences[sentence_index]
            class_1 = False
            for token in nlp(sentence):
                # class 1: location is object of company or vice versa
                if token.dep_ in deps and token.text in article_countries:
                    cur.execute("INSERT INTO company_location (company, location, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s,  %s)", (company[0], token.text, 1, 0, article[1]))
                    class_1 = True
            # class 2: no specific relationship, but appear in the same sentence
            if not class_1:
                cur.execute("INSERT INTO company_location (company, location, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (company[0], get_location(article_locations, sentence_index), 2, 0, article[1]))
            remove_location(article_locations, sentence_index)
        article_companies.remove(company)
    closest_entity(article_companies, article_chemicals, article_locations)

    if article_count % 300 == 0:
        conn.commit()

conn.commit()

cur.close()
conn.close()
