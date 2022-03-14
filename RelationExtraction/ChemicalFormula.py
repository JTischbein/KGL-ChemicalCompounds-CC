import sys

sys.path.append("../")

from Database import Database

db = Database("../config.ini").connect

db_table = "chemical_location_relations"

if db == None:
    print("Connection failure")
    sys.exit()

def line(l):
    synonym = l[0]
    formula = l[1]

    db.execute('UPDATE ' + db_table + ' SET chemical_formula = %s WHERE synonym = %s', attributes=(formula, synonym))

db.execute_and_run('SELECT DISTINCT synonym, chemical_formula FROM chemicals', callback=line, progress_bar=True)