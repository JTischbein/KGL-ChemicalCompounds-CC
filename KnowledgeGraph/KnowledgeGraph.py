from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class KnowledgeGraph:
    """
    Class for providing an interface to the Neo4j database
    ...
    
    Attributes
    ----------
    driver : neo4j.v1.GraphDatabase.driver
        The driver for the Neo4j database   
    
    Methods
    -------
    init : Initialize the driver
    close : Close the driver
    create_entity : Create an entity
    create_relationship : Create a relationship
    find_entity : Find an entity
    delete_entity : Delete an entity
    delete_relationship : Delete a relationship between two entities
    delete : Delete all entities
    custom_query : Execute a custom query
    """
    def __init__(self, uri, user, password):
        """
        Initialize the driver
        ...

        Parameters
        ----------
        uri : str
            The URI of the Neo4j database
        user : str
            User log in credentials
        password : str
            password log in credentials
        
        Returns
        -------
        None
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """"
        Closes the driver connection. Don't forget to call this method when you are finished with it.
        ...

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.driver.close()

    def create_entity(self, name, label, synonyms=None):
        """
        Creates an entity with a given name and label.
        Calls the _create_and_return_entity method which returns the created entity.
        ...

        Parameters
        ----------
        name : str
            name of the entity
        label : str
            label of the entity
        synonyms : list
            optional argument. We mainly use it here to store the different mentions of the same chemical compound

        Returns
        -------
        None
        """
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
        """"
        Creates an edge between two presaved entities. The edge is built upon the found the predetermined relationship between the two entities.
        Calls the _create_and_return_relationship method which returns the nodes of the created relationship.

        Parameters
        ----------
        subject : str
            name of the subject (outgoing edge) entity
        subjectLabel : str
            label of the subject entity
        relation : str
            label of the relationship
        object : str
            name of the object (incoming edge) entity
        objectLabel : str
            label of the object entity
        hierarchy_class : list
            list of hierarchy classes found
        hierarchy_count : list
            number of occurences for each hierarchy class
        word_gap : int
            number of sentences between the third class relations

        Returns
        -------
        None
        """
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
        """
        Finds an entity with a given name and label.
        Calls the _find_entity method which returns the name of the found entity.
        ...

        Parameters
        ----------
        name : str
            name of the entity
        label : str
            label of the entity

        Returns
        -------
        None
        """
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_entity, name, label)

    @staticmethod
    def _find_and_return_entity(tx, name, label):
        result = tx.run("MATCH (a:%s) WHERE a.name = %s RETURN a.name AS name, a.label AS label" % (name, label))

        return [row["name"] for row in result]

    def delete_entity(self, name, label):
        """
        Deletes an entity with a given name and label.
        ...

        Parameters
        ----------
        name : str
            name of the entity
        label : str
            label of the entity

        Returns
        -------
        None
        """
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_entity, name, label)

    @staticmethod
    def _delete_entity(tx, name, label):
        result = tx.run("MATCH (a:%s) WHERE a.name = %s DELETE a" % (name, label))

    def delete_relationship(self, subject, subjectLabel, relation, object, objectLabel):
        """
        Deletes an edge between two presaved entities. The edge is built upon the found the predetermined relationship between the two entities.
        ...

        Parameters
        ----------
        subject : str
            name of the subject (outgoing edge) entity
        subjectLabel : str
            label of the subject entity
        relation : str
            label of the relationship
        object : str
            name of the object (incoming edge) entity
        objectLabel : str
            label of the object entity

        Returns
        -------
        list of subject and object 
        """
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_relationship, subject, subjectLabel, relation, object, objectLabel)

    @staticmethod
    def _delete_relationship(tx, subject, subjectLabel, relation, object, objectLabel):
        result = tx.run("MATCH (a:%s)-[r:%s]->(b:%s) WHERE a.name = %s AND b.name = %s DELETE r" % (subjectLabel, relation, objectLabel, subject, object))

    def delete_all(self):
        """
        Deletes all entities and thus clears the entire graph. Use with caution!
        ...

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_all_entities)
    
    @staticmethod
    def _delete_all_entities(tx):
        tx.run("MATCH (n) DETACH DELETE n")

    def custom_query(self, query):
        """
        Executes a custom query.
        ...

        Parameters
        ----------
        query : str
            query to be executed

        Returns
        -------
        Whatever is defined in the return statement of the query
        """
        with self.driver.session() as session:
            result = session.write_transaction(self._custom_query, query)
            return result

    @staticmethod
    def _custom_query(tx, query):
        result = tx.run(query)

        return [row for row in result]
