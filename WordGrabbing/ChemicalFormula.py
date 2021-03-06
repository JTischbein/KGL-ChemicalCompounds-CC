# This script adds to all chemicals in the chemicals table the chemical formula.
# We get the formulas by quering wikidata with the chemical synonym.

from re import sub
import sys
sys.path.append('../')

from lodstorage.query import Query
from lodstorage.sparql import SPARQL

from Database import Database

# Connect to database
db = Database('../config.ini').connect()

# Get chemical formula of chemical tag
def grab_formula(tag):
    substanceQueryStr = """
        SELECT DISTINCT ?entry
        WHERE {
        wd:%s wdt:P274 ?entry.
        }
    """

    substanceQueryStr %= (tag)

    endpoint = SPARQL("https://query.wikidata.org/sparql")

    try:
        query = Query(query=substanceQueryStr,
                        name="ChemicalFormulas",
                        lang="sparql")
        queryResLoD = endpoint.queryAsListOfDicts(query.query)

        return queryResLoD[0]['entry']
    except:
        print("Error, element", tag, "has no chemical formula")
        return None


def iteration(line):
    link = line[0]
    synonym = line[1]
    tag = line[2]

    # Get chemical formula
    chemical_formula = grab_formula(tag)
    
    # Save chemical formula in DB
    if chemical_formula:
        db.execute('UPDATE chemicals SET chemical_formula = %s WHERE link = %s AND synonym = %s AND tag = %s', (chemical_formula, link, synonym, tag))
    

# Run iteration for every chemical
db.execute_and_run('SELECT * FROM chemicals', callback=iteration, progress_bar=True)

def set_formula_as_synonym(line):
    db.execute('UPDATE chemicals SET chemical_formula = %s WHERE synonym = %s', attributes=(line[1], line[1]))

db.execute_and_run('SELECT * FROM chemicals WHERE chemical_formula IS NULL;', callback=set_formula_as_synonym, progress_bar=True)