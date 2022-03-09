# KGL-ChemicalCompounds-CC


## Table of Contents
- [General](#general)
- [Databases](#databases)
- [Link Grabbing](#link-grabbing)

## General

This is the Repository of the Knowledge Graph Lab. Goal was the creation of a Knowledge Graph for relations between companies, their use of chemical compounds and their production site locations. The result is a collection of scripts, which build step for step databases with the needed informations. 

Every script can be run alone when the needed environment variables are set. In the following every step for running the script and therefore building the knowledge graph are described.

IMPORTANT: To run the scripts properly and every path works correctly, you have to be in the directory of the script and then run it.

## Packages and Environmental Variables

To get all needed packages, we added a requirements.txt. To install these, just run:
```
pip install requirements.txt
# or if pip3 is used
pip3 install requirements.txt
```
For some scripts there is additionally `selenium` needed. All variables are specified in the `config.ini`.

## Databases

As Databases we use Postgres and Neo4j. Both run in Docker Containers. To initiate a Postgres container, just run:
```
# Get the Image
docker pull postgres
# Run container
docker run --name KGLPG --restart=always -e POSTGRES_PASSWORD=<PW> -d -p <PORT>:5432 -v /opt/PG/database:/var/lib/postgresql/data postgres
```
Replace `<PW>` with an own password and `<Port>` with an open port on your machine. For Neo4j run:
```
# Get the Image
docker pull neo4j
# Run container
docker run --name KGLNEO --restart=always -p<PORT1>:7474 -p<PORT2>:7687 -d -v $HOME/neo4j/data:/data -v $HOME/neo4j/logs:/logs -v $HOME/neo4j/import:/var/lib/neo4j/import -v $HOME/neo4j/plugins:/plugins --env NEO4J_AUTH=neo4j/<PW> neo4j:latest
```
`<PORT1>` is for the web interface and `<Port2>` is for the database itself.

We use 2 python classes for interaction with the databases. For Postgres the `database.py`, which is used in every script. This class needs the packages `tqdm` and `psycopg2` (both can be installed with `pip`). For Neo4j we have the `KnowledgeGraph.py` in the folder Knowledge Graph. Thic class only needs `neo4j` as package (can be installed with `pip`).

For specifying the login credentials and IP + Port, edit the `config.ini`.

### Database Credentials in Scripts

To specify the credentials for the scripts, rename the `config.ini.example` to `config.ini` and edit the content for Postgres and !!! TODO !!! Neo4j Credentials.

## Link Grabbing

The Link Grabbing part crawls the websites for links to articles and saves them in the Postgres database. In the `ChemietechnikURLs.txt` are all article listings from chemietechnik.de listed.

For executing `LinksChemietechnik.py` you need the following additional packages:
```
requests
beautifulsoup4
```
For executing `LinksChemanager.py` and `LinksIHS.py` you need an instance of selenium running. If wanted, you can use a docker instance of selenium ([GitHub](https://github.com/SeleniumHQ/docker-selenium)) and additionally `tqdm` for progress indication.

## ContentGrabbing

For all scripts these packages are needed:
```
tqdm
newspaper
```
For `ContentChemanager.py` and `ContentICIS.py` you need additionally `selenium`.

##