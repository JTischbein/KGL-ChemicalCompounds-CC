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
        graph.create_entity(chemical[0], "chemical_compound", chemical[2])
    
    # Add all locations to the graph
    cur.execute("SELECT DISTINCT synonym FROM locations")
    locations = cur.fetchall()
    locations = [location[0] for location in locations] 
    for location in tqdm(locations):
        graph.create_entity(location, "Location")

    # Add company->chemical relationships
    cur.execute("SELECT DISTINCT cc.company, cc.hierarchy, cc.word_gap, cc.chemical FROM company_chemical cc INNER JOIN company_wikidata cw on cc.company = cw.name;")
    company_chemical = cur.fetchall()
    for company_chemical in tqdm(company_chemical):
        graph.create_relationship(company_chemical[0], "Company", "PRODUCES", company_chemical[1], company_chemical[2], company_chemical[3], "chemical_compound")

    # Add company->location relationships
    cur.execute("SELECT DISTINCT cc.company, cc.hierarchy, cc.word_gap, cc.location, cc.article FROM company_location cc INNER JOIN company_wikidata cw on cc.company = cw.name;")
    company_location = cur.fetchall()
    for company_location in tqdm(company_location):
        graph.create_relationship(company_location[0], "Company", "LOCATED_IN", company_location[1], company_location[2], company_location[3], "Location")

    graph.close()