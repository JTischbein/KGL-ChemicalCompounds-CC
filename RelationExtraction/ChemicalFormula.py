import sys
sys.path.append("../")

from Database import Database

db = Database("../config.ini").connect()

db_table = "company_chemical_relations"

if db == None:
    print("Connection failure")
    sys.exit()

def line(l):
    synonym = l[0]
    formula = l[1]

    db.execute('UPDATE company_chemical_relations SET chemical_formula = %s WHERE chemical = %s', attributes=(formula, synonym))
    db.execute('UPDATE chemical_location_relations SET chemical_formula = %s WHERE chemical = %s', attributes=(formula, synonym))

db.execute_and_run('SELECT DISTINCT synonym, chemical_formula FROM chemicals', callback=line, progress_bar=True)
