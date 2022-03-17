# Genrating plots for the presentation and the report

from configparser import ConfigParser
from dis import dis
from html import entities
import psycopg2
import matplotlib.pyplot as plt
import os
from neo4j import GraphDatabase
import sys
import numpy as np

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

sys.path.append("../")
from Database import Database
from KnowledgeGraph.KnowledgeGraph import KnowledgeGraph


try:
    os.mkdir("plots")
    print("Directory " , "plots" ,  " Created ")
except FileExistsError:
    print("Directory " , "plots" ,  " already exists")


db = Database("../config.ini").connect()

if db == None: 
    print("Cannot connect to Postgres database")
    sys.exit()




oa_chem_count = db.execute("SELECT COUNT(*) FROM chemicals")
oa_comp_count = db.execute("SELECT COUNT(*) FROM companies")
oa_loca_count = db.execute("SELECT COUNT(*) FROM locations")

dis_chem_count = db.execute("SELECT COUNT(*) FROM (SELECT DISTINCT chemical_formula FROM chemicals) sub")
dis_comp_count = db.execute("SELECT COUNT(*) FROM (SELECT DISTINCT tag FROM companies) sub")
dis_loca_count = db.execute("SELECT COUNT(*) FROM (SELECT DISTINCT iso FROM locations) sub")


labels = ['chemicals', 'companies', 'locations']
distinct = [dis_chem_count, dis_comp_count, dis_loca_count]
distinct = [dis[0][0] for dis in distinct]
overall = [oa_chem_count, oa_comp_count, oa_loca_count]
overall = [ov[0][0] for ov in overall]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, distinct, width, label='Distinct')
rects2 = ax.bar(x + width/2, overall, width, label='All')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Total')
ax.set_title('Word occurrence per category')
ax.set_xticks(x, labels)
ax.legend()

ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)

fig.tight_layout()

plt.savefig("plots/wordspercat.png")


entities = db.execute("SELECT synonym, COUNT(synonym) FROM companies GROUP BY synonym ORDER BY COUNT(synonym) DESC LIMIT 101")

indices = np.arange(0,21) * 5

names = [str(i) + ": " + entities[i][0] for i in indices]
count = [entities[i][1] for i in indices]


fig, ax = plt.subplots()
x = np.arange(len(names))

width = 0.25
rects1 = ax.bar(x, count, width)

plt.bar(names, count)
plt.title("Companies Occurrences")
plt.xlabel("")
plt.ylabel("Total Occurrences")
plt.xticks(rotation = 90)
ax.bar_label(rects1, padding=3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# alternate option without .gcf
plt.subplots_adjust(bottom=0.35)
plt.savefig("plots/companiescount0-100-5.png")


config = ConfigParser()
config.read("../config.ini")

driver = GraphDatabase.driver(config["NEO4J"]["GRAPH_HOST"], auth=(config["NEO4J"]["GRAPH_USER"], config["NEO4J"]["GRAPH_PASSWORD"]))


article_distribution = db.execute("""
        SELECT COUNT(link)
        FROM articles
        WHERE (link LIKE '%ihsmarkit.com%') OR (link LIKE '%icis.com%') OR (link LIKE '%chemietechnik.de%') OR (link LIKE '%chemanager-online.com%')
        GROUP BY CASE
            WHEN link LIKE '%chemietechnik.de%' THEN 'chemietechnik.de'
            WHEN link LIKE '%chemanager-online.com%' THEN 'chemanager-online.com'
            WHEN link LIKE '%ihsmarkit.com%' THEN 'ihsmarkit.com'
            WHEN link LIKE '%icis.com%' THEN 'icis.com'
        END
        """)
article_distribution = [x[0] for x in article_distribution]
print(article_distribution)

plt.figure()
plt.pie(article_distribution, labels = ['chemietechnik.de', 'chemanager-online.com', 'ihsmarkit.com', 'icis.com'], autopct='%1.1f%%')
plt.title("Article Distribution")
plt.savefig("plots/article_distribution.png")


location_distribution = db.execute("""
        SELECT iso, COUNT(synonym)
        FROM locations
        GROUP BY iso
        HAVING COUNT(synonym) > 50
        ORDER BY COUNT(synonym) DESC
""")
location_name = [x[0] for x in location_distribution]
location_count = [x[1] for x in location_distribution]
#print(location_distribution)

plt.figure()
plt.bar(location_name, location_count)
plt.xticks(rotation=90)
plt.title("Location Distribution")
plt.ylabel("Number of articles")
plt.savefig("plots/location_distribution.png")



company_chemical_distribution = db.execute("""
        SELECT hierarchy, COUNT(hierarchy)
        FROM company_chemical
        GROUP BY hierarchy
        ORDER BY COUNT(hierarchy) ASC
""")
company_chemical_name = [x[0] for x in company_chemical_distribution]
company_chemical_count = [x[1] for x in company_chemical_distribution]
print(company_chemical_distribution)

plt.figure()
plt.subplot(1, 2, 1)
plt.pie(company_chemical_count, labels = company_chemical_name, autopct='%1.1f%%')
plt.title("company->chemical")



company_location_distribution = db.execute("""
        SELECT hierarchy, COUNT(hierarchy)
        FROM company_location
        GROUP BY hierarchy
        ORDER BY COUNT(hierarchy) ASC
""")

company_location_name = [x[0] for x in company_location_distribution]
company_location_count = [x[1] for x in company_location_distribution]
print(company_location_distribution)

plt.subplot(1, 2, 2)
plt.pie(company_location_count, labels = company_location_name, autopct='%1.1f%%')
plt.title("company->location")

plt.savefig("plots/hierarchies.png")

with driver.session() as session:
    carcinogen_waste = session.run("MATCH (n:Waste) WHERE n.carcinogen = 'YES' RETURN SUM(toInteger(n.total_releases_in_pounds)) AS sum, n.year AS year")
    carcinogen_waste = [[int(row["sum"]), row["year"]] for row in carcinogen_waste]
    carcinogen_waste_year = [row[1] for row in carcinogen_waste]
    carcinogen_waste_sum = [row[0] for row in carcinogen_waste]

    plt.figure()
    plt.bar(carcinogen_waste_year, carcinogen_waste_sum)
    plt.title("Carcinogenic Waste Year Distribution")
    plt.ylabel("Waste in pounds")
    plt.savefig("plots/carcinogenic_waste_year_distribution.png")


with driver.session() as session:
    waste = session.run("MATCH (n:Waste) WHERE n.carcinogen = 'NO' RETURN SUM(toInteger(n.total_releases_in_pounds)) AS sum, n.year AS year")
    waste = [[int(row["sum"]), row["year"]] for row in waste]
    waste_year = [row[1] for row in waste]
    waste_sum = [row[0] for row in waste]

    plt.figure()
    plt.bar(waste_year, waste_sum)
    plt.title("Non-Carcinogenic Waste Year Distribution")
    plt.ylabel("Waste in pounds")
    plt.savefig("plots/non_carcinogenic_waste_year_distribution.png")
  
with driver.session() as session:
    findings_amount = []
    findings_value = []
    for i in range(1, 11):
        finding = session.run("MATCH (p) WHERE size((p)-[:CONTAINS]->()) = %s RETURN count(p) AS amount" % i)
        finding = [int(row["amount"]) for row in finding]
        findings_amount.append(finding[0])
        findings_value.append("%d" % i)

    plt.figure()
    plt.bar(findings_value, findings_amount)
    plt.title("Findings in Articles Distribution")
    plt.ylabel("Findings")
    plt.savefig("plots/findings_in_articles_distribution.png")

db.disconnect()
