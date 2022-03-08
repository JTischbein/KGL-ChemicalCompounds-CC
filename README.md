# KGL-ChemicalCompounds-CC


## Table of Contents
  - [Databases](#databases)
  - [Link Grabbing](#link-grabbing)


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

### Database Credentials in Scripts

To specify the credentials for the scripts, rename the `dbcfg.ini.example` to `dbcfg.ini` and edit the content for Postgres and !!! TODO !!! Neo4j Credentials.

## Link Grabbing

The Link Grabbing part crawls the websites for links to articles and saves them in the Postgres database. In the `ChemietechnikURLs.txt` are all article listings from chemietechnik.de listed.
