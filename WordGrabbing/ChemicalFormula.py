from re import sub
import sys
sys.path.append('../')

from lodstorage.query import Query
from lodstorage.sparql import SPARQL

from Database import Database

db = Database('../dbcfg.ini').connect()

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
        entries = [record for record in queryResLoD]

        return queryResLoD[0]['entry']
    except:
        print("Fehler:", tag)
        return None


def iteration(line):
    link = line[0]
    synonym = line[1]
    tag = line[2]

    chemical_formula = grab_formula(tag)
    
    if chemical_formula:
        db.execute('UPDATE chemicals SET chemical_formula = %s WHERE link = %s AND synonym = %s AND tag = %s', (chemical_formula, link, synonym, tag))
    


db.execute_and_run('SELECT * FROM chemicals', callback=iteration, progress_bar=True)