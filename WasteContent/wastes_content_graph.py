import csv
from neo4j import GraphDatabase
import re

HOST_GRAPH = ""
USER_GRAPH = ""
PASSWORD_GRAPH = ""

CSV_LINK = ""

def get_company_wastes(company_name, file):
    rows = []

    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader: rows.append(row)

        # of form (database company name, csv company name, year, chemical, total releases, total recycled)
        wastes = []

        for name in company_name:
            for row in rows:
                pat = re.compile("(.*? |^)%s( .*?|$)" % name)
                found = False
                try:
                    if re.fullmatch(pat, row[14]):
                        found = True;
                        where = row[14]
                    elif re.fullmatch(pat, row[16]):
                        found = True;
                        where = row[16]
                    if found: wastes.append(
                        (name, where, int(row[0]), row[33], float(row[102]), float(row[110]) + float(row[111])))
                except IndexError:
                    continue
        print(len(wastes))
        print(wastes)

        return wastes


def get_companies_years_waste(wastes):
    year_wastes = []

    for waste in wastes:
        found = False
        for year_waste in year_wastes:
            if all([waste[0] == year_waste[0], waste[2] == year_waste[2], waste[3] == year_waste[3]]):
                year_waste[4] += waste[4]
                year_waste[5] += waste[5]
                found = True
                break
        if not found: year_wastes.append(list(waste))

    print(len(year_wastes))
    print(year_wastes)
    return year_wastes


def get_graph_companies(driver):
    query = (
        "MATCH (c:Company) RETURN c.name as name"
    )

    company_name = driver.session().run(query)

    return [row["name"] for row in company_name]


def insert_graph_data(driver, data_list):
    wasteID = 0
    for data in data_list:
        if int(data[4]) or int(data[5]):
            with driver.session() as session:
                session.run(
                    "CREATE (a:Waste {wasteID: '%d', year: '%d', chemical: '%s', total_releases_in_pounds:'%d', total_recycling_in_pounds: '%d'})" % (
                    wasteID, data[2], data[3], data[4], data[5]))
                session.run(
                    "MATCH (a:Waste {wasteID: '%d'}), (b:Company {name: '%s'}) CREATE (b)-[r:RESPONSIBLE_FOR]->(a)" % (
                    wasteID, data[0]))

                wasteID += 1


if __name__ == "__main__":
    driver = GraphDatabase.driver(HOST_GRAPH, auth=(USER_GRAPH, PASSWORD_GRAPH))
    insert_graph_data(driver, get_companies_years_waste(
        get_company_wastes(get_graph_companies(driver), CSV_LINK)))
    driver.close()