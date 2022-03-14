import spacy

# creates a noun list for each sentence
def get_nouns(sentences, nlp):
    nouns = []
    for sentence in sentences:
        doc = nlp(sentence)
        nouns.append([chunk.text for chunk in doc.noun_chunks])
    return nouns 

# Allows us to fetch all companies, chemicals and locations from the article
def get_all_entities(noun_sentences, companies, chemicals, locations):
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

# Use this function to return a reduced set for chemical->location relation
def get_entities(noun_sentences, chemicals, locations):
    chemical_list = []
    location_list = []
    for idx, sentence in enumerate(noun_sentences):
        for noun in sentence:
            if noun in chemicals:
                chemical_list.append((noun, idx))
            elif noun in locations:
                location_list.append((noun, idx))
    return chemical_list, location_list 

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
def closest_entity_all(article_companies, article_chemicals, article_locations, chemical_dictionary, article, cur):
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
        cur.execute("INSERT INTO company_chemical_relations (company, chemical, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (company[0], chemical_dictionary[closest_chemical[0]], 3, chemical_distance, article[1]))
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
        cur.execute("INSERT INTO company_location_relations (company, location, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (company[0], closest_location[0], 3, location_distance, article[1]))
        article_locations.remove(closest_location)

# For the entities which are left over, we would like to calculate the distance between the entity (chemical or location) and the company
def closest_entity(article_chemicals, article_locations, chemical_dictionary, cur, article):
    # We have to find the closest location to the chemical
    for chemical in article_chemicals:
        if not article_locations:
            break
        closest_location = article_locations[0]
        location_distance = abs(chemical[1] - closest_location[1])
        for location in article_locations:
            if abs(chemical[1] - location[1]) < location_distance:
                closest_location = location
                location_distance = abs(chemical[1] - location[1])
        cur.execute("INSERT INTO chemical_location_relations (chemical, location, hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)", (chemical_dictionary[chemical[0]], closest_location[0], 3, location_distance, article[1]))
        article_locations.remove(closest_location)

english_deps = ["nsubj", "nsubj_pass", "dobj", "iobj", "pobj"]
german_deps = ["sb", "sbp", "oa", "og", "op"]

english_nlp = spacy.load("en_core_web_trf")
german_nlp = spacy.load("de_dep_news_trf")
