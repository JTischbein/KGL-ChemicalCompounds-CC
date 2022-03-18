# Getting data from postgres database, restructure them and save them in the neo4j database

from configparser import ConfigParser
from tqdm import tqdm
import sys
sys.path.append("../")
from Database import Database
from KnowledgeGraph import KnowledgeGraph





if __name__ == "__main__":

    db = Database("../config.ini").connect()

    config = ConfigParser()
    config.read("../config.ini")
    
    graph = KnowledgeGraph(config["NEO4J"]["GRAPH_HOST"], config["NEO4J"]["GRAPH_USER"], config["NEO4J"]["GRAPH_PASSWORD"])

    graph.delete_all()

    # Add all companies to the graph
    companies = db.execute("SELECT DISTINCT synonym FROM companies")

    companies = [company[0] for company in companies]
    print("Adding companies to the graph")
    for company in tqdm(companies):
        graph.create_entity(company, "Company")
    
    # Add all chemicals to the graph
    chemicals = db.execute("SELECT ch.chemical_formula, ch.tag, array_agg(DISTINCT ch2.synonym) FROM chemicals ch LEFT JOIN chemicals ch2 ON ch.chemical_formula = ch2.chemical_formula GROUP BY ch.chemical_formula, ch.tag")

    chemicals = [chemical for chemical in chemicals if chemical[0] is not None]
    print("Adding chemicals to the graph")
    for chemical in tqdm(chemicals):
        graph.create_entity(chemical[0], "chemical_compound", synonyms=chemical[2])
    
    # Add all locations to the graph
    locations = db.execute("SELECT iso, array_agg(DISTINCT synonym) FROM locations GROUP BY iso;")
    
    print("Adding locations to the graph") 
    for location in tqdm(locations):
        graph.create_entity(location[0], "Location", synonyms=locations[1])

    # Add company->chemical relationships
    company_chemical = db.execute("""SELECT company, chemical_formula, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT company, chemical_formula, hierarchy, count(hierarchy) as hcount, AVG(word_gap) as wg
                FROM company_chemical_relations INNER JOIN (SELECT * FROM articles WHERE release_date >= '2015-01-01') a ON company_chemical_relations.article = a.link
                GROUP BY company, chemical_formula, hierarchy
                ORDER BY company, chemical_formula, hierarchy) tab INNER JOIN companies_wikidata cw ON tab.company = cw.name
                GROUP BY company, chemical_formula""")
                
    chemical_gap = [float(gap[4][0]) for gap in company_chemical]
    print("Adding company->chemical relationships")
    for company_chemical, gap in tqdm(zip(company_chemical, chemical_gap)):
        graph.create_relationship(company_chemical[0], "Company", "PRODUCES", company_chemical[1], "chemical_compound", company_chemical[2], company_chemical[3], gap)

    # Add company->location relationships
    company_location = db.execute("""SELECT company, iso, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT company, iso, hierarchy, count(hierarchy) as hcount, AVG(word_gap) as wg
                FROM company_location_relations INNER JOIN (SELECT * FROM articles WHERE release_date >= '2015-01-01') a ON company_location_relations.article = a.link
                GROUP BY company, iso, hierarchy
                ORDER BY company, iso, hierarchy) tab INNER JOIN companies_wikidata cw ON tab.company = cw.name
                GROUP BY company, iso""")
                
    location_gap = [float(gap[4][0]) for gap in company_location]
    print("Adding company->location relationships")
    for company_location, gap in tqdm(zip(company_location, location_gap)):
        graph.create_relationship(company_location[0], "Company", "LOCATED_IN", company_location[1], "Location", company_location[2], company_location[3], gap)

    # Add chemical->location relationships
    chemical_location = db.execute("""SELECT chemical_formula, iso, array_agg(hierarchy) as hierarchy, array_agg(hcount) as count, array_agg(wg) as word_gap FROM (
                SELECT chemical_formula, iso, hierarchy, COUNT(hierarchy) as hcount, AVG(word_gap) as wg
                FROM chemical_location_relations INNER JOIN (SELECT * FROM articles WHERE release_date >= '2015-01-01') a ON chemical_location_relations.article = a.link
                GROUP BY chemical_formula, iso, hierarchy
                ) sub
                GROUP BY chemical_formula, iso""")
                
    location_gap = [float(gap[4][0]) for gap in chemical_location]
    print("Adding chemical->location relationships")
    for chemical_location, gap in tqdm(zip(chemical_location, location_gap)):
        graph.create_relationship(chemical_location[0], "chemical_compound", "PRODUCED_IN", chemical_location[1], "Location", chemical_location[2], chemical_location[3], gap)

    graph.close()