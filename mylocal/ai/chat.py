import os

from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI


class Neo4jQueryProcessor:
    def __init__(self):
        self.graph = None
        self.chain = None
        self.setup_neo4j_connection()

    def setup_neo4j_connection(self):
        url = os.getenv("NEO4J_MYLOCAL_DB_URI")
        username = os.getenv("NEO4J_MYLOCAL_USERNAME")
        password = os.getenv("NEO4J_MYLOCAL_PASSWORD")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not all([url, username, password, openai_api_key]):
            raise ValueError("Missing required environment variables")

        self.graph = Neo4jGraph(url=url, username=username, password=password)

        # Initialize the QA chain with OpenAI
        self.chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(temperature=0),
            graph=self.graph,
            verbose=True,
            validate_cypher=True,
            allow_dangerous_requests=True  # Acknowledge the risks
        )

    def query(self, question: str):
        if not self.chain:
            raise ValueError("Chain not initialized. Check Neo4j connection.")
        
        return self.chain.run(question)
