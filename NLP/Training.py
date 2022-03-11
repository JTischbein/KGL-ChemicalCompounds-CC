from sre_constants import IN
from spacy.training.example import Example
from html import entities
from re import L
import sys
sys.path.append('../')
from Database import Database 


db = Database('../config.ini').connect()

TRAIN_DATA = []

def find_next(text, pos, char):
    for i in range(pos, len(text)):
        if text[i] == char: return i
    return len(text)

def run(line):
    global TRAIN_DATA
    
    synonym = line[1]
    sentence = line[2]
    position = line[3]

    i = 0

    entities = []

    for pos in position:
        i = sentence.find(synonym, i)
        if i == -1: return
        j = i + len(synonym)
        if j >= len(sentence):
            pass
        elif not sentence[j].lower() in "abcdefghijklmnopqrstuvwxyzöäü":
            sentence = sentence[:j] + " " + sentence[j+1:]
        else:
            j = find_next(sentence, j, " ")

        entities.append((i,  j, "ORG"))
        i += len(synonym)

    TRAIN_DATA.append(
        (sentence, {"entities": entities})
    )

db.execute_and_run('SELECT * FROM (SELECT * FROM companies_training_data INNER JOIN articles ON companies_training_data.link = articles.link WHERE language = %s) ctd INNER JOIN company_wikidata cw on ctd.synonym = cw.name;', attributes=("de",), callback=run, progress_bar=True)


print(TRAIN_DATA[0])

############################################
############################################
############################################

import spacy
nlp = spacy.load("de_core_news_sm")

TRAIN_DATA_EXAMPLE = [
              ("Walmart is a leading e-commerce company", {"entities": [(0, 7, "ORG")]}),
              ("I reached Chennai yesterday.", {"entities": [(18, 27, "GPE")]}),
              ("I recently ordered a book from Amazon", {"entities": [(31,37, "ORG")]}),
              ("I was driving a BMW", {"entities": [(16,19, "PRODUCT")]}),
              ("I ordered this from ShopClues", {"entities": [(20,29, "ORG")]}),
              ("Fridge can be ordered in Amazon ", {"entities": [(0,6, "PRODUCT"), (25,31, "ORG")]}),
              ("Flipkart started it's journey from zero", {"entities": [(0,8, "ORG")]}),
              ("I recently ordered from Max", {"entities": [(24,27, "ORG")]}),
              ("Flipkart is recognized as leader in market",{"entities": [(0,8, "ORG")]}),
              ("I recently ordered from Swiggy", {"entities": [(24,29, "ORG")]})
              ]

pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
print(unaffected_pipes)



ner=nlp.get_pipe("ner")


# Adding labels to the `ner`
for _, annotations in TRAIN_DATA:
  for ent in annotations.get("entities"):
    ner.add_label(ent[2])


import random
from spacy.util import minibatch, compounding
from pathlib import Path

# TRAINING THE MODEL
with nlp.disable_pipes(*unaffected_pipes):

  # Training for 30 iterations
  for iteration in range(30):

    # shuufling examples  before every iteration
    random.shuffle(TRAIN_DATA)
    losses = {}
    # batch up the examples using spaCy's minibatch
    batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))

    for batch in batches:
        texts, annotations = zip(*batch)
        examples = []
        for i in range(len(texts)):
            doc = nlp(texts[i])
            example = Example.from_dict(doc, annotations[i])
            examples.append(example)

        try:
            nlp.update(
                examples,
                drop=0.5,  # dropout - make it harder to memorise data
                losses = losses,
            )
        except Exception as e:
            print(e)
            print(texts, annotations)
            print("\n\n\n-----------------\n\n\n")

    # for text, entities in TRAIN_DATA:
    #     print("\n\n\n-----------------\n\n\n")
    #     doc = nlp(text)
    #     print("text:", text)
    #     print("ent:", entities)
    #     for e in entities["entities"]:
    #         print(text[e[0]:e[1]])
    #     example = Example.from_dict(doc, entities)

    #     nlp.update(
    #         [example],
    #         drop=0.5,  # dropout - make it harder to memorise data
    #         losses = losses,
    #     )        

    # for batch in batches:
    #     texts, annotations = zip(*batch)
    #     print("texts:", texts)
    #     print("annotations:", annotations)
    #     for i in range(len(texts)):

    #     nlp.update(
    #                 texts,  # batch of texts
    #                 annotations,  # batch of annotations
    #                 drop=0.5,  # dropout - make it harder to memorise data
    #                 losses = losses,
    #             )
    #     print("Losses", losses)









# Testing the model
doc = nlp("I was driving a Alto")
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])

# Save the  model to directory
output_dir = Path('/content/')
nlp.to_disk(output_dir)
print("Saved model to", output_dir)

# Load the saved model and predict
print("Loading from", output_dir)
nlp_updated = spacy.load(output_dir)
doc = nlp_updated("Fridge can be ordered in FlipKart" )
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])