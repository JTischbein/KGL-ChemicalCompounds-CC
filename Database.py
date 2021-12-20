from configparser import ConfigParser
import psycopg2


def progressBar(iterable, lenit, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = lenit

    # Progress Bar Printing Function
    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()


class Database:
    def __init__(self, config_path):
        config = ConfigParser()
        config.read(config_path)
        self.host = config["DEFAULT"]["HOST"]
        self.port = config["DEFAULT"]["PORT"]
        self.dbname = config["DEFAULT"]["DBNAME"]
        self.user = config["DEFAULT"]["USER"]
        self.pw = config["DEFAULT"]["PASSWORD"]

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
        self.cursor.execute(sql, attributes)
        if fetch and self.cursor.rowcount == -1:
            return self.cursor.fetchall()
        return None

    def execute_and_run(self, sql, attributes=None, callback=lambda line: print(line), progress_bar=True):
        with self.connection.cursor() as cur:
            cur.execute(sql, tuple(attributes))
            size = cur.rowcount
            if cur.rowcount > 0:
                if progress_bar:
                    for l in (progressBar(cur, size, prefix='Progress:', suffix='Complete', length=50) if progress_bar else cur):
                        callback(l)


    def add_article(self, link, article="", release_date=""):
        sql = "INSERT INTO articles (link, content, release_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        self.execute(sql, (link, article, release_date), fetch=False)

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
        self.execute('INSERT INTO ' + topic + ' (link, synonym, tag) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
                     (link, synonym, tag), fetch=False)
