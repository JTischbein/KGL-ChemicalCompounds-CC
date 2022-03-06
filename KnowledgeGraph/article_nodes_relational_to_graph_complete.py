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
    cur.execute("SELECT DISTINCT * FROM articles")
    articles = cur.fetchall()
    articleID = 0 # eigentlich Abfrage der derzeit höchsten ArticleID
    print(len(articles))
    for article in articles:
        graph.write(articleID, article[0], article[1], article[2], article[3])
        articleID += 1

    cur.close()
    conn.close()

    graph.close()
