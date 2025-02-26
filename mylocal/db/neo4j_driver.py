import pandas as pd
from neo4j import GraphDatabase


class Neo4jDriver:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def driver(self):
        return self._driver

    def close(self):
        self._driver.close()

    def insert_node(self, tx, label, properties):
        query = f"MERGE (n:{label} {{id: $id}}) " + "".join(
            [f"SET n.{k} = ${k} " for k in properties.keys() if k != "id"]
        )
        tx.run(query, **properties)

    def insert_relationship(self, tx, from_label, to_label, relationship, from_id, to_id):
        query = (
            f"MATCH (a:{from_label} {{id: $from_id}}), (b:{to_label} {{id: $to_id}}) "
            f"MERGE (a)-[:{relationship}]->(b)"
        )
        tx.run(query, from_id=from_id, to_id=to_id)

    def process_file(self, file_path, governing_type, parent_key):
        """
        Process a file to create GoverningBody nodes with specified type and relationships.
        
        Args:
            file_path (str): Path to the TSV file
            governing_type (str): Type of the governing body
            parent_key (str): Column name that contains the parent node's ID
        """
        df = pd.read_csv(file_path, sep="\t")
        with self._driver.session() as session:
            for _, row in df.iterrows():
                properties = row.dropna().to_dict()
                properties['type'] = governing_type
                
                # Create or update the node
                session.execute_write(self.insert_node, "GoverningBody", properties)
                
                # Create relationship if parent key exists and is not null
                if parent_key and parent_key in row and pd.notna(row[parent_key]):
                    session.execute_write(
                        self.insert_relationship, 
                        "GoverningBody", "GoverningBody", "GOVERNED_BY", 
                        row["id"], row[parent_key]
                    )

    def execute_query(self, query, parameters=None):
        """
        Execute a read query and return the results.

        Args:
            query (str): The Cypher query to execute
            parameters (dict, optional): Query parameters. Defaults to None.

        Returns:
            list: List of records from the query result
        """
        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

    def execute_read_query(self, query, parameters=None):
        """
        Execute a read-only query in a read transaction.

        Args:
            query (str): The Cypher query to execute
            parameters (dict, optional): Query parameters. Defaults to None.

        Returns:
            list: List of records from the query result
        """
        with self._driver.session() as session:
            return session.execute_read(lambda tx: [record for record in tx.run(query, parameters or {})])
