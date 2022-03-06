import psycopg2
import matplotlib.pyplot as plt
import os

import config

try:
    os.mkdir("plots")
    print("Directory " , "plots" ,  " Created ") 
except FileExistsError:
    print("Directory " , "plots" ,  " already exists")

conn = psycopg2.connect(host=config.host, port=config.port, dbname=config.dbname, user=config.user, password=config.password)

cur = conn.cursor()

cur.execute("""
        SELECT COUNT(link)
        FROM articles
        WHERE (link LIKE '%ihsmarkit.com%') OR (link LIKE '%icis.com%') OR (link LIKE '%chemietechnik.de%') OR (link LIKE '%chemanager-online.com%')
        GROUP BY CASE
            WHEN link LIKE '%ihsmarkit.com%' THEN 'ihsmarkit.com'
            WHEN link LIKE '%icis.com%' THEN 'icis.com'
            WHEN link LIKE '%chemietechnik.de%' THEN 'chemietechnik.de'
            WHEN link LIKE '%chemanager-online.com%' THEN 'chemanager-online.com'
        END
        """)       

article_distribution = cur.fetchall()
article_distribution = [x[0] for x in article_distribution]
print(article_distribution)

plt.figure()
plt.pie(article_distribution, labels = ['ihsmarkit.com', 'icis.com', 'chemietechnik.de', 'chemanager-online.com'], autopct='%1.1f%%')
plt.title("Article Distribution")
plt.savefig("plots/article_distribution.png")


cur.execute("""
        SELECT iso, COUNT(synonym)
        FROM locations
        GROUP BY iso
        HAVING COUNT(synonym) > 50
        ORDER BY COUNT(synonym) DESC
""")

location_distribution = cur.fetchall()
location_name = [x[0] for x in location_distribution]
location_count = [x[1] for x in location_distribution]
#print(location_distribution)

plt.figure()
plt.bar(location_name, location_count)
plt.xticks(rotation=90)
plt.title("Location Distribution")
plt.ylabel("Number of articles")
plt.savefig("plots/location_distribution.png")


cur.execute("""
        SELECT hierarchy, COUNT(hierarchy)
        FROM company_chemical
        GROUP BY hierarchy
        ORDER BY COUNT(hierarchy) ASC
""")

company_chemical_distribution = cur.fetchall()
company_chemical_name = [x[0] for x in company_chemical_distribution]
company_chemical_count = [x[1] for x in company_chemical_distribution]
print(company_chemical_distribution)

plt.figure()
plt.subplot(1, 2, 1)
plt.pie(company_chemical_count, labels = company_chemical_name, autopct='%1.1f%%')
plt.title("company->chemical")


cur.execute("""
        SELECT hierarchy, COUNT(hierarchy)
        FROM company_location
        GROUP BY hierarchy
        ORDER BY COUNT(hierarchy) ASC
""")

company_location_distribution = cur.fetchall()
company_location_name = [x[0] for x in company_location_distribution]
company_location_count = [x[1] for x in company_location_distribution]
print(company_location_distribution)

plt.subplot(1, 2, 2)
plt.pie(company_location_count, labels = company_location_name, autopct='%1.1f%%')
plt.title("company->location")

plt.savefig("plots/hierarchies.png")


cur.close()
conn.close()