import psycopg2

from tqdm import tqdm

import config
from KnowledgeGraph import KnowledgeGraph

conn = psycopg2.connect(host=config.host, port=config.port, dbname=config.dbname, user=config.user, password=config.password)

cur = conn.cursor()

if __name__ == "__main__":
    
    graph = KnowledgeGraph(config.GraphUri, config.GraphUser, config.GraphPassword)

    graph.delete()

    # Add all companies to the graph
    cur.execute("SELECT DISTINCT companies.synonym FROM companies INNER JOIN company_wikidata cd on companies.synonym = cd.name;")
    companies = cur.fetchall()
    companies = [company[0] for company in companies]
    for company in tqdm(companies):
        graph.create_entity(company, "Company")
    
    # Add all chemicals to the graph
    cur.execute("SELECT ch.chemical_formula, ch.tag, array_agg(DISTINCT ch2.synonym) FROM chemicals ch LEFT JOIN chemicals ch2 ON ch.chemical_formula = ch2.chemical_formula GROUP BY ch.chemical_formula, ch.tag")
    chemicals = cur.fetchall()
    chemicals = [chemical for chemical in chemicals if chemical[0] is not None]
    for chemical in chemicals:
        graph.create_entity(chemical[0], "chemical_compound", synonyms=chemical[2])
    
    # Add all locations to the graph
    cur.execute("SELECT DISTINCT synonym FROM locations")
    locations = cur.fetchall()
    locations = [location[0] for location in locations] 
    for location in tqdm(locations):
        graph.create_entity(location, "Location")

    # Add company->chemical relationships
    cur.execute("""SELECT company, chemical, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT company, chemical, hierarchy, count(hierarchy) as hcount, AVG(word_gap) as wg
                FROM company_chemical
                GROUP BY company, chemical, hierarchy
                ORDER BY company, chemical, hierarchy) tab INNER JOIN company_wikidata cw ON tab.company = cw.name
                GROUP BY company, chemical""")
    company_chemical = cur.fetchall()
    chemical_gap = [float(gap[4][0]) for gap in company_chemical]
    for company_chemical in tqdm(company_chemical):
        graph.create_relationship(company_chemical[0], "Company", "PRODUCES", company_chemical[1], "chemical_compound", company_chemical[2], company_chemical[3], chemical_gap)

    # Add company->location relationships
    cur.execute("""SELECT company, location, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT company, location, hierarchy, count(hierarchy) as hcount, AVG(word_gap) as wg
                FROM company_location
                GROUP BY company, location, hierarchy
                ORDER BY company, location, hierarchy) tab INNER JOIN company_wikidata cw ON tab.company = cw.name
                GROUP BY company, chemical""")
    company_location = cur.fetchall()
    location_gap = [float(gap[4][0]) for gap in company_location]
    for company_location in tqdm(company_location):
        graph.create_relationship(company_location[0], "Company", "LOCATED_IN", company_location[1], "Location", company_location[2], company_location[3], location_gap)

    graph.close()