from neo4j import GraphDatabase
from Database import Database

class KGL_graph:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def write_node(self, articleID, link, content, date, language):
        with self.driver.session() as session:
            session.run("CREATE (a:Article {ArticleID: '%d', link:'%s', content: '%s', date: '%s', language: '%s'})" % (articleID, link, content.replace("'", ""), date, language))


    def write_relation(self, contents, type):
        with self.driver.session() as session:
            for content in contents:
                    if not [row["relation"] for row in session.run("MATCH (a:Article {link: '%s'}), (b:Company {name: '%s'}), p=(a)-[r:CONTAINS]->(b) RETURN p AS relation" % (content[0], content[1].replace("'", "")))]:
                        session.run("MATCH (a:Article {link: '%s'}), (b:Company {name: '%s'}) CREATE (a)-[r:CONTAINS]->(b)" % (content[0], content[1].replace("'", "")))

                    if not [row["relation"] for row in session.run("MATCH (a:Article {link: '%s'}), (b:%s WHERE '%s' IN b.synonyms), p=(a)-[r:CONTAINS]->(b) RETURN p AS relation" % (content[0], type, content[2]))]:
                        session.run("MATCH (a:Article {link: '%s'}), (b:%s WHERE '%s' IN b.synonyms) CREATE (a)-[r:CONTAINS]->(b)" % (content[0], type, content[2]))


if __name__ == "__main__":
    db = Database("../config.ini").connect()

    config = ConfigParser()
    config.read("../config.ini")
    
    graph = KGL_graph(config["NEO4J"]["GRAPH_HOST"], config["NEO4J"]["GRAPH_USER"], config["NEO4J"]["GRAPH_PASSWORD"])
    
    articles = []

    articles += db.execute("SELECT DISTINCT articles.link, articles.content, articles.release_date, articles.language FROM (articles INNER JOIN chemical_location_relations ON articles.link = chemical_location_relations.article)")
    articles += db.execute("SELECT DISTINCT articles.link, articles.content, articles.release_date, articles.language FROM (articles INNER JOIN company_chemical_relations ON articles.link = company_chemical_relations.article)")
    articles += db.execute("SELECT DISTINCT articles.link, articles.content, articles.release_date, articles.language FROM (articles INNER JOIN company_location_relations ON articles.link = company_location_relations.article)")
    articles = list(dict.fromkeys(articles))  # herausfiltern aller article die Verknüpfungen zu mindestens 2 der 3 entities haben
    articleID = 0 # eigentlich Abfrage der derzeit höchsten ArticleID
    
    for article in articles:
        graph.write_node(articleID, article[0], article[1], article[2], article[3])
        articleID += 1

    company_location_relation = db.execute("SELECT DISTINCT article, company, location FROM company_location_relations")
    graph.write_relation(company_location_relation, "Location")

    company_chemical_relation = db.execute("SELECT DISTINCT article, company, chemical FROM company_chemical_relations")
    graph.write_relation(company_chemical_relation, "chemical_compound")

    chemical_location_relation = db.execute("SELECT DISTINCT article, chemical, location FROM chemical_location_relations")
    graph.write_relation(chemical_location_relation, "Location")

    chemical_location_relation = db.execute("SELECT DISTINCT article, location, chemical FROM chemical_location_relations")
    graph.write_relation(chemical_location_relation, "chemical_compound")



    db.close()

    graph.close()
