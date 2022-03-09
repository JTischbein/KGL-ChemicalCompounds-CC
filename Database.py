from configparser import ConfigParser
import psycopg2
from tqdm import tqdm


class Database:
    def __init__(self, config_path):
        config = ConfigParser()
        config.read(config_path)
        self.host = config["POSTGRES"]["HOST"]
        self.port = config["POSTGRES"]["PORT"]
        self.dbname = config["POSTGRES"]["DBNAME"]
        self.user = config["POSTGRES"]["USER"]
        self.pw = config["POSTGRES"]["PASSWORD"]

        self.connection = None
        self.cursor = None
    

    def connect(self):
        if self.connection is not None:
            return None
        try:
            self.connection = psycopg2.connect(host=self.host, port=self.port, dbname=self.dbname,
                                               user=self.user, password=self.pw)
            self.cursor = self.connection.cursor()
            self.connection.autocommit = True
        except Exception as e:
            print(e)
            return None
        return self

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def execute(self, sql, attributes=None, fetch=True):
        with self.connection.cursor() as cur:
            cur.execute(sql, attributes)
            if not fetch: return None
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return None

    def execute_and_run(self, sql, attributes=[], callback=lambda line: print(line), progress_bar=False):
        with self.connection.cursor() as cur:
            cur.execute(sql, tuple(attributes))
            size = cur.rowcount
            if cur.rowcount > 0:
                if progress_bar:
                    for l in (cur if not progress_bar else tqdm(cur, total=cur.rowcount)):
                        callback(l)

    def add_article(self, link, article="", release_date=""):
        sql = "INSERT INTO articles (link, release_date) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        self.execute(sql, (link, release_date), fetch=False)

    def update_article(self, link, content=None, release_date=None):
        if content is None and release_date is None:
            return
        elif release_date is None:
            self.execute("UPDATE articles SET content = %s WHERE link = %s", (content, link))
        elif content is None:
            self.execute("UPDATE articles SET release_date = %s WHERE link = %s", (release_date, link))
        else:
            self.execute("UPDATE articles SET content = %s, release_date = %s WHERE link = %s",
                         (content, release_date, link))

    def add_word(self, topic, link, synonym, tag):
        self.execute('INSERT INTO ' + topic + ' (link, synonym, tag) VALUES (%s, %s, %s)',
                     (link, synonym, tag), fetch=False)

    def set_language(self, link, language):
        self.execute("UPDATE articles SET language = %s WHERE link = %s", (language, link))

    def add_word_to_dict(self, table_name, word, tag, synonym="", synonym_id=-1):
        self.execute('INSERT INTO ' + table_name + ' (name, tag) VALUES (%s, %s) ON CONFLICT DO NOTHING', (word, tag))
