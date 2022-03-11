# KGL-ChemicalCompounds-CC


## Table of Contents
- [General](#general)
- [Packages and Environmental Variables](#packages-and-environmental-variables)
- [Databases](#databases)
- [Database Credentials in Scripts](#database-credentials-in-scripts)
- [Link Grabbing](#link-grabbing)
- [Content Grabbing](#content-grabbing)
- [Language](#language)
- [Word Grabbing](#word-grabbing)
- [Relation Extraction](#relation-extraction)
- [Knowledge Graph](#knowledge-graph)

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

For `spacy` pretrained models are needed. To install these, just run:
```
python -m spacy download en_core_web_trf
python -m spacy download de_dep_news_trf
```

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

To recreate our database schema of the relational database:
```
CREATE TABLE public.articles (
    link text NOT NULL,
    content text,
    release_date date,
    language text
);

CREATE TABLE public.companies_wikidata (
    tag text NOT NULL,
    name text NOT NULL
);

CREATE TABLE public.chemicals (
    link text,
    synonym text,
    tag text,
    chemical_formula text
);

CREATE TABLE public.companies (
    link text,
    synonym text,
    tag text
);

CREATE TABLE public.locations (
    link text,
    synonym text,
    iso text
);


CREATE TABLE public.company_chemical_relations (
    company text,
    chemical text,
    hierarchy integer,
    word_gap integer,
    article text
);

CREATE TABLE public.company_location_relations (
    company text,
    location text,
    hierarchy_level integer,
    word_gap integer,
    article text
);

CREATE TABLE public.chemical_location_relations (
    chemical text,
    location text,
    hierarchy_level integer,
    word_gap integer,
    article text
);

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT article_pk PRIMARY KEY (link);
```

### Database Credentials in Scripts

To specify the credentials for the scripts, rename the `config.ini.example` to `config.ini` and edit the content for Postgres and !!! TODO !!! Neo4j credentials.

## Link Grabbing

The Link Grabbing part crawls the websites for links to articles and saves them in the Postgres database. In the `ChemietechnikURLs.txt` are all article listings from chemietechnik.de listed. Our ICIS Link Grabbing script does not work anymore, as the website got changed and our inital crawling solution is now deprecated.

For executing `LinksChemietechnik.py` you need the following additional packages:
```
requests
beautifulsoup4
```
For executing `LinksChemanager.py` and `LinksIHS.py` you need an instance of selenium running. If wanted, you can use a docker instance of selenium ([GitHub](https://github.com/SeleniumHQ/docker-selenium)).

## Content Grabbing

In the Content Grabbing part we open the crawled links and extract the text of the article.
For all scripts the package `newspaper3k` is needed. For `ContentChemanager.py` and `ContentICIS.py` you need additionally `selenium`.

When crawling, we often get the same article from different links. To delete all duplicates, run the `article_content_uniquifier.py` oder run the following SQL Query, which detects duplicates and only keeps the article with the lexicographical first or minimum link:
```
DELETE FROM articles WHERE link NOT IN (
    SELECT min(link) as link FROM articles GROUP BY content
    );
```

## Language 

In our further analysis, we use NLP. To select the right model for the articles, we need the language. In the Language folder are several scripts which iterate over the articles, detect their languages (only German or English, as we have no other sources) and save an abbreviation ("de" or "en") in the database.

TODO SKRIPT

## Word Grabbing

In this step, we search for companies, locations and chemicals in the articles.

### Companies

For the companies we use a listing of chemical companies from WikiData. For speed reasons we store in advance all companies in the database. This task is performed by the script `CompaniesWikidata.py` (If wanted, there is a script to just use the biggest chemical companies from Wikipedia). To run it, you need the package `pylodstorage` ([GitHub](https://github.com/WolfgangFahl/pyLoDStorage)) for quering Wikidata.

If all companies are in the database, the script `DatabaseCompanyGrabbing.py` can extract all company occurrences in the articles. It also uses `spacy`.

### Locations

For the locations we used a fairly simple approach, as every little step in direction of more complex locations brought us tons of trash data. In the end we focused on countries with a predefined dict. To extract all locations and save them in the database, you need to run `LocationGrabber.py`.

### Chemicals

For the chemical detection we query Wikidata. This task is performed by the script `WikidataChemicalGrabbing.py`. Here we need the packages `spacy` and `pylodstorage`. To add the associated chemical formulas to the found synonyms, you can run `ChemicalFormula.py`, which also queries Wikidata.

## Relation Extraction

To extract all relations between the three categories companies, locations and chemicals, run `RelationExtraction.py`. !!! TODO !!!

## Knowledge Graph

The whole database structure can be converted into a Neo4j graph database. For this, we have the scripts `DatabaseTranslation.py` and !!! TODO !!!
