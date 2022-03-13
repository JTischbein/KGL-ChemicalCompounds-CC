from configparser import ConfigParser
import psycopg2
from tqdm import tqdm


class Database:
    """
    Class for providing an interface to the Postgres database
    ...
    
    Attributes
    ----------
    host : str
        The address of the Postgres database
    port : str
        The port of the Postgres database
    dbname : str
        The name of the used database
    user : str
        The user credentials
    pw : str
        The password credentials
    connection : psycopg2.connection
        The connection object of psycopg2
    cursor : psycopg2.cursor
        The cursor object of psycopg2
    
    Methods
    -------
    init : Initialize the static attributes
    connect : Connect to database
    disconnt : Disconnect from database
    execute : Execute a SQL query
    execute_and_run : Execute a SQL query and callback for every row
    add_article : Adds article
    update_article : Updates article
    add_word_to_dict : Adds word 
    set_language : Sets language of article
    """
    def __init__(self, config_path):
        """__init__ Initializes the class

        Args:
            config_path (str): Path to config file
        """
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
        """connect Connects to othe database

        Returns:
            Database: Returns the object itself
        """
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
        """disconnect Disconnects from the database
        """
        self.cursor.close()
        self.connection.close()

    def execute(self, sql, attributes=None, fetch=True):
        """execute Executes SQL query

        Args:
            sql (str): SQL query
            attributes (list, optional): Attributes of the SQL query. Defaults to None.
            fetch (bool, optional): Boolean, if result of query should be returned. Defaults to True.

        Returns:
            _type_: _description_
        """
        with self.connection.cursor() as cur:
            cur.execute(sql, attributes)
            if not fetch: return None
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return None

    def execute_and_run(self, sql, attributes=[], callback=lambda line: print(line), progress_bar=False):
        """execute_and_run Executes SQl query and callback for every row

        Args:
            sql (str): SQL query
            attributes (list, optional): Attributes of the SQL query. Defaults to [].
            callback (method, optional): Callback method for every row (gets called with one argument, the row). Defaults to lambdaline:print(line).
            progress_bar (bool, optional): Boolean whether a progress indicator should be displayed. Defaults to False.
        """
        with self.connection.cursor() as cur:
            cur.execute(sql, tuple(attributes))
            size = cur.rowcount
            if cur.rowcount > 0:
                if progress_bar:
                    for l in (cur if not progress_bar else tqdm(cur, total=cur.rowcount)):
                        callback(l)

    def add_article(self, link, article="", release_date=""):
        """add_article Adds article to database

        Args:
            link (str): Link of the article
            article (str, optional): Content of the article. Defaults to "".
            release_date (str, optional): Release date of the article. Defaults to "".
        """
        sql = "INSERT INTO articles (link, release_date) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        self.execute(sql, (link, release_date), fetch=False)

    def update_article(self, link, content="", release_date=""):
        """update_article Updates article in database

        Args:
            link (str): Link of the article
            article (str, optional): Content of the article. Defaults to "".
            release_date (str, optional): Release date of the article. Defaults to "".
        """
        if content is None and release_date is None:
            return
        elif release_date is None:
            self.execute("UPDATE articles SET content = %s WHERE link = %s", (content, link))
        elif content is None:
            self.execute("UPDATE articles SET release_date = %s WHERE link = %s", (release_date, link))
        else:
            self.execute("UPDATE articles SET content = %s, release_date = %s WHERE link = %s",
                         (content, release_date, link))

    def set_language(self, link, language):
        """set_language Sets language of article

        Args:
            link (str): Hyperlink of article
            language (str): Language of article
        """
        self.execute("UPDATE articles SET language = %s WHERE link = %s", (language, link))

    def add_word_to_dict(self, table_name, word, tag):
        """add_word_to_dict Add word to database

        Args:
            table_name (str): Name of the table in the database
            word (str): The word to save
            tag (str): Wikidata tag of the word
        """
        self.execute('INSERT INTO ' + table_name + ' (name, tag) VALUES (%s, %s) ON CONFLICT DO NOTHING', (word, tag))
