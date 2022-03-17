# Adding the location ISO to relation tables 

import sys
sys.path.append("../")
from Database import Database

db = Database("../config.ini").connect()

if db == None:
    print("Connection Error, quitting")
    sys.exit()


def cb(line):
    iso = line[0]
    synonym = line[1]

    db.execute("UPDATE company_location_relations SET iso = %s WHERE location = %s", (iso, synonym))
    db.execute("UPDATE chemical_location_relations SET iso = %s WHERE location = %s", (iso, synonym))

db.execute_and_run("SELECT DISTINCT iso, synonym FROM locations", attributes=(), callback=cb, progress_bar=True)

