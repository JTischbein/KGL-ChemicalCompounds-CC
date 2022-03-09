from Database import Database

db = Database('dbcfg.ini').connect()

#deletes one entry if two have the same content
db.execute("""DELETE FROM articles WHERE link NOT IN (
    SELECT min(link) as link FROM articles GROUP BY content
    );""")