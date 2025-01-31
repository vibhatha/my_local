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

    def process_file(self, file_path, node_label, parent_key, parent_label):
        df = pd.read_csv(file_path, sep="\t")
        with self._driver.session() as session:
            for _, row in df.iterrows():
                properties = row.dropna().to_dict()
                session.execute_write(self.insert_node, node_label, properties)
                if parent_key in row and pd.notna(row[parent_key]):
                    session.execute_write(
                        self.insert_relationship, node_label, parent_label, "GOVERNED_BY", row["id"], row[parent_key]
                    )
