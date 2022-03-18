# Getting waste data from an other source than the newspaper articles.
# This script crawls the tri_2016-2020_us.zip file

import csv
from neo4j import GraphDatabase
import re
from configparser import ConfigParser

config = ConfigParser()
config.read("../config.ini")

CSV_LINK = ""


def get_company_wastes(company_name, file):
    rows = []

    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader: rows.append(row)

        # of form (database company name, csv company name, year, chemical, total releases, total recycled, measurement_unit, carcinogen)
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
                        (name, where, int(row[0]), row[33], float(row[102]), float(row[110]) + float(row[111]), row[45], row[42]))
                except IndexError:
                    continue

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
                    "CREATE (a:Waste {wasteID: '%d', year: '%d', chemical: '%s', total_releases:'%d', total_recycling: '%d', measurement_unit: '%s', carcinogen: '%s'})" % (
                    wasteID, data[2], data[3], data[4], data[5], data[6], data[7]))
                
                session.run(
                    "MATCH (a:Waste {wasteID: '%d'}), (b:Company {name: '%s'}) CREATE (b)-[r:RESPONSIBLE_FOR]->(a)" % (
                    wasteID, data[0]))

                wasteID += 1


if __name__ == "__main__":
    driver = GraphDatabase.driver(config["NEO4J"]["GRAPH_HOST"], auth=(config["NEO4J"]["GRAPH_USER"], config["NEO4J"]["GRAPH_PASSWORD"]))
    insert_graph_data(driver, get_companies_years_waste(
        get_company_wastes(get_graph_companies(driver), config["WASTE"]["CSV_PATH"])))
    driver.close()
