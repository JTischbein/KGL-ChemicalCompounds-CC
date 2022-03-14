from subprocess import call
import sys
sys.path.append("../")

import spacy
import nltk
nltk.download("punkt")
from nltk import tokenize

from Database import Database

english_deps = ["nsubj", "nsubj_pass", "dobj", "iobj", "pobj"]
german_deps = ["sb", "sbp", "oa", "og", "op"]

english_nlp = spacy.load("en_core_web_trf")
german_nlp = spacy.load("de_dep_news_trf")

db1 = "companies"
db2 = "locations"
name1 = "company"
name2 = "location"
rel_table = "company_location_relations"

db = Database("../config.ini").connect()

if db == None:
    print("Connection failure")
    sys.exit()

def detect_occurences(syn1, syn2, sentences):
    occ1 = []
    occ2 = []

    for i, sentence in enumerate(sentences):
        if syn1 in sentence:
            occ1.append(i)
        if syn2 in sentence:
            occ2.append(i)

    # company BASF: [1,4,7], location De:; [2,4,8] = (1,2),(1,4),(1,8)(4,2)(4,4)(4,8)...
    
    return occ1, occ2

def check_coherence(syn1, syn2, sentence, language):
    if language == 'de':
        nlp = german_nlp
        deps = german_deps
    else:
        nlp = english_nlp
        deps = english_deps

    doc = nlp(sentence)

    for token in doc:
        if token.dep_ in deps and (syn1 in token.text or syn2 in token.text):
            return True

    return False

    

def save_in_db(syn1, syn2, hierarchy, word_gap, link):
    db.execute('INSERT INTO ' + rel_table + ' ( ' + name1 + ', ' + name2 + ', hierarchy, word_gap, article) VALUES (%s, %s, %s, %s, %s)', attributes=(syn1, syn2, hierarchy, word_gap, link))

def line(l):
    link = l[0]
    syn1 = l[1]
    syn2 = l[2]
    text = l[3]
    language = l[4]

    sentences = nltk.sent_tokenize(text)
    occ1, occ2 = detect_occurences(syn1, syn2, sentences)

    min_hierarchy = 4
    min_word_gap = 9999999

    for pos1 in occ1:
        for pos2 in occ2:
            hierarchy = 0
            word_gap = 0
            if pos1 == pos2:
                if check_coherence(syn1, syn2, sentences[pos1], language):
                    hierarchy = 1
                else:
                    hierarchy = 2
            else:
                hierarchy = 3
                word_gap = abs(pos1 - pos2)
            if min_hierarchy > hierarchy:
                min_hierarchy = hierarchy
            if min_word_gap > word_gap:
                min_word_gap = word_gap
            
    save_in_db(syn1, syn2, min_hierarchy, min_word_gap, link)



db.execute_and_run("SELECT DISTINCT a.link as link, a.synonym, b.synonym, art.content, art.language FROM " + db1 + " a INNER JOIN " + db2 + " b ON a.link = b.link INNER JOIN articles art ON a.link = art.link;", callback=line, progress_bar=True)