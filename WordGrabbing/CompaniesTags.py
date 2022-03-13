import sys
sys.path.append("../")
from Database import Database

db = Database("../config.ini").connect()

if db == None:
    print("Connection Error, quitting")
    sys.exit()


def cb(line):
    tag = line[0]
    name = line[1]

    db.execute("UPDATE companies SET tag = %s WHERE synonym = %s", (tag, name))

db.execute_and_run("SELECT * FROM companies_wikidata", attributes=(), callback=cb, progress_bar=True)

