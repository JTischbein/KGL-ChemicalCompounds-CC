import sys
sys.path.append('../')
from Database import Database
from lodstorage.query import Query
from lodstorage.sparql import SPARQL


substanceQueryStr = """
    SELECT ?company ?companyLabel (group_concat(?instanceOfLabel;separator=',') as ?instanceOfLabels)
    WHERE {
    ?company wdt:P452 wd:Q207652.  
    ?company rdfs:label ?companyLabel filter (lang(?companyLabel) = "en"). 
    ?company wdt:P31 ?instanceOf.
    ?instanceOf rdfs:label ?instanceOfLabel filter (lang(?instanceOfLabel) = "en"). 
    } 
    GROUP BY ?company ?companyLabel
    ORDER BY ?companyLabel
"""

endpoint = SPARQL("https://query.wikidata.org/sparql")

query = Query(query=substanceQueryStr,
                  name="Recognized chemical compounds",
                  lang="sparql")
queryResLoD = endpoint.queryAsListOfDicts(query.query)
entries = [(record.get('company'), record.get('companyLabel')) for record in queryResLoD]


db = Database('../dbcfg.ini').connect()

for tag, word in entries:
    tag = tag.split("/")[-1]
    db.add_word_to_dict('companies_wikidata', word, tag)

