from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class KnowledgeGraph:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_entity(self, name, label, synonyms=None):
        name = name.replace("'", "")
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_entity, name, label, synonyms)

    @staticmethod
    def _create_and_return_entity(tx, name, label, synonyms):
        if synonyms is None:
            result = tx.run("CREATE (a: %s {name: '%s'}) RETURN a.name AS name, labels(a) AS label" % (label, name))
        else:
            synonyms = '['+', '.join(synonyms)+']'
            result = tx.run("CREATE (a: %s {name: '%s', synonyms: %s}) RETURN a.name AS name, a.synonym AS synonym labels(a) AS label" % (label, name, synonyms))
        return result.single()

    def create_relationship(self, subject, subjectLabel, relation, object, objectLabel, hierarchy_class, hierarchy_count, word_gap):
        subject = subject.replace("'", "")
        hierarchy_class = '['+', '.join(hierarchy_class)+']'
        hierarchy_count = '['+', '.join(hierarchy_count)+']'
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_relationship, subject, subjectLabel, relation, object, objectLabel, hierarchy_class, hierarchy_count, word_gap)

    @staticmethod
    def _create_and_return_relationship(tx, subject, subjectLabel, relation, object, objectLabel, hierarchy_class, hierarchy_count, word_gap):
        result = tx.run("MATCH (a:%s {name: '%s'}), (b:%s {name: '%s'}) CREATE (a)-[r:%s {hierarchy_level: %s, hierarchy_count: %s, word_gap: %d}]->(b) RETURN a, b" % (subjectLabel, subject, objectLabel, object, relation, hierarchy_class, hierarchy_count, word_gap))

        return [{"a": row["a"]["name"], "b": row["b"]["name"]} for row in result]

    def find_entity(self, name, label):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_entity, name, label)

    @staticmethod
    def _find_and_return_entity(tx, name, label):
        result = tx.run("MATCH (a:%s) WHERE a.name = %s RETURN a.name AS name, a.label AS label" % (name, label))

        return [row["name"] for row in result]

    def delete(self):
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_entities)
    
    @staticmethod
    def _delete_entities(tx):
        tx.run("MATCH (n) DETACH DELETE n")