import os
import pytest
from mylocal.db.neo4j_driver import Neo4jDriver
from mylocal.db.connect import ConnectorManager
from neo4j.exceptions import ServiceUnavailable

def test_neo4j_connection():
    # Get Neo4j connection details from environment variables
    uri = os.getenv("NEO4J_MYLOCAL_DB_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_MYLOCAL_USERNAME", "neo4j")
    password = os.getenv("NEO4J_MYLOCAL_PASSWORD")
    
    if not password:
        pytest.skip("NEO4J_MYLOCAL_PASSWORD environment variable is not set")

    try:
        connector_manager = ConnectorManager()
        
        # Using context manager for Neo4jDriver
        with Neo4jDriver(uri, username, password) as neo4j_driver:
            connector_manager.register_connector("neo4j", neo4j_driver)
            
            # Test the connection by running a simple query
            with neo4j_driver.driver.session() as session:
                result = session.run("RETURN 1 + 1 as sum")
                record = result.single()
                assert record["sum"] == 2
                
    except ServiceUnavailable:
        pytest.fail("Could not connect to Neo4j database. Make sure the database is running.")
    except Exception as e:
        pytest.fail(f"Failed to connect to Neo4j: {str(e)}")
