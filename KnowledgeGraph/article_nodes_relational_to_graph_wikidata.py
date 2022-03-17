# Add only articles to neo4j which occur in relations and are from wikidata

from neo4j import GraphDatabase
import psycopg2

HOST = ""
PORT = ""
DBNAME = ""
USER = ""
PASSWORD = ""

HOST_GRAPH = ""
USER_GRAPH = ""
PASSWORD_GRAPH = ""

class KGL_graph:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def write(self, articleID, link, content, date, language):
        with self.driver.session() as session:
            session.run("CREATE (a:Article {ArticleID: '%d', link:'%s', content: '%s', date: '%s', language: '%s'})" % (articleID, link, content.replace("'", ""), date, language))


if __name__ == "__main__":
    graph = KGL_graph(HOST_GRAPH, USER_GRAPH, PASSWORD_GRAPH)

    conn = psycopg2.connect(host=HOST, port=PORT, dbname=DBNAME, user=USER,
                            password=PASSWORD)
    cur = conn.cursor()
    articles = []
    cur.execute("SELECT DISTINCT articles.link, articles.content, articles.release_date, articles.language FROM ((company_wikidata INNER JOIN companies ON company_wikidata.name = companies.synonym) INNER JOIN articles ON articles.link = companies.link)")
    articles += cur.fetchall()
    cur.execute(
        "SELECT DISTINCT articles.link, articles.content, articles.release_date, articles.language FROM company_location INNER JOIN articles ON articles.link = company_location.article")
    articles += cur.fetchall()
    cur.execute(
        "SELECT DISTINCT articles.link, articles.content, articles.release_date, articles.language FROM company_chemical INNER JOIN articles ON articles.link = company_chemical.article")
    articles += cur.fetchall()
    articles = list(dict.fromkeys(articles))  # herausfiltern aller article die Verknüpfungen zu mindestens 2 der 3 entities haben
    articleID = 0 # eigentlich Abfrage der derzeit höchsten ArticleID

    for article in articles:
        graph.write(articleID, article[0], article[1], article[2], article[3])
        articleID += 1

    cur.close()
    conn.close()

    graph.close()
