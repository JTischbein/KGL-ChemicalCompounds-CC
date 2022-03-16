import psycopg2

from tqdm import tqdm

import config
from KnowledgeGraph import KnowledgeGraph

conn = psycopg2.connect(host=config.host, port=config.port, dbname=config.dbname, user=config.user, password=config.password)

cur = conn.cursor()

if __name__ == "__main__":
    
    graph = KnowledgeGraph(config.GraphUri, config.GraphUser, config.GraphPassword)

    graph.delete_all()

    # Add all companies to the graph
    cur.execute("SELECT DISTINCT companies.synonym FROM companies INNER JOIN companies_wikidata cd on companies.synonym = cd.name;")
    companies = cur.fetchall()
    companies = [company[0] for company in companies]
    print("Adding companies to the graph")
    for company in tqdm(companies):
        graph.create_entity(company, "Company")
    
    # Add all chemicals to the graph
    cur.execute("SELECT ch.chemical_formula, ch.tag, array_agg(DISTINCT ch2.synonym) FROM chemicals ch LEFT JOIN chemicals ch2 ON ch.chemical_formula = ch2.chemical_formula GROUP BY ch.chemical_formula, ch.tag")
    chemicals = cur.fetchall()
    chemicals = [chemical for chemical in chemicals if chemical[0] is not None]
    print("Adding chemicals to the graph")
    for chemical in tqdm(chemicals):
        graph.create_entity(chemical[0], "chemical_compound", synonyms=chemical[2])
    
    # Add all locations to the graph
    cur.execute("SELECT DISTINCT synonym FROM locations")
    locations = cur.fetchall()
    locations = [location[0] for location in locations]
    print("Adding locations to the graph") 
    for location in tqdm(locations):
        graph.create_entity(location, "Location")

    # Add company->chemical relationships
    cur.execute("""SELECT company, chemical_formula, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT company, chemical_formula, hierarchy, count(hierarchy) as hcount, AVG(word_gap) as wg
                FROM company_chemical_relations INNER JOIN (SELECT * FROM articles WHERE release_date >= '2015-01-01') a ON company_chemical_relations.article = a.link
                GROUP BY company, chemical_formula, hierarchy
                ORDER BY company, chemical_formula, hierarchy) tab INNER JOIN companies_wikidata cw ON tab.company = cw.name
                GROUP BY company, chemical_formula""")
    company_chemical = cur.fetchall()
    chemical_gap = [float(gap[4][0]) for gap in company_chemical]
    print("Adding company->chemical relationships")
    for company_chemical, gap in tqdm(zip(company_chemical, chemical_gap)):
        graph.create_relationship(company_chemical[0], "Company", "PRODUCES", company_chemical[1], "chemical_compound", company_chemical[2], company_chemical[3], gap)

    # Add company->location relationships
    cur.execute("""SELECT company, iso, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT company, iso, hierarchy, count(hierarchy) as hcount, AVG(word_gap) as wg
                FROM company_location_relations INNER JOIN (SELECT * FROM articles WHERE release_date >= '2015-01-01') a ON company_location_relations.article = a.link
                GROUP BY company, iso, hierarchy
                ORDER BY company, iso, hierarchy) tab INNER JOIN companies_wikidata cw ON tab.company = cw.name
                GROUP BY company, iso""")
    company_location = cur.fetchall()
    location_gap = [float(gap[4][0]) for gap in company_location]
    print("Adding company->location relationships")
    for company_location, gap in tqdm(zip(company_location, location_gap)):
        graph.create_relationship(company_location[0], "Company", "LOCATED_IN", company_location[1], "Location", company_location[2], company_location[3], gap)

    # Add chemical->location relationships
    cur.execute("""SELECT chemical_formula, iso, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT chemical_formula, iso, hierarchy, COUNT(hierarchy) as hcount, AVG(word_gap) as wg
                FROM chemical_location_relations INNER JOIN (SELECT * FROM articles WHERE release_date >= '2015-01-01') a ON chemical_location_relations.article = a.link
                GROUP BY chemical_formula, iso, hierarchy
                ) sub
                GROUP BY chemical_formula, iso""")
    chemical_location = cur.fetchall()
    location_gap = [float(gap[4][0]) for gap in chemical_location]
    print("Adding chemical->location relationships")
    for chemical_location, gap in tqdm(zip(chemical_location, location_gap)):
        graph.create_relationship(chemical_location[0], "chemical_compound", "PRODUCED_IN", chemical_location[1], "Location", chemical_location[2], chemical_location[3], gap)

    graph.close()