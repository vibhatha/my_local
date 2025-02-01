import os

from langchain_core.language_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI


class AIModelFactory:
    @staticmethod
    def get_model(model_name: str) -> BaseChatModel:
        if model_name == "openai":
            return ChatOpenAI(temperature=0)
        elif model_name == "deepseek":
            return ChatDeepSeek(
                model="deepseek-chat",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )
        else:
            raise ValueError(f"Unknown AI model: {model_name}")


class Neo4jQueryProcessor:
    def __init__(self, model_name: str):
        self.graph = None
        self.chain = None
        self.ai_model: BaseChatModel = AIModelFactory.get_model(model_name)
        self.setup_neo4j_connection()

    def setup_neo4j_connection(self):
        url = os.getenv("NEO4J_MYLOCAL_DB_URI")
        username = os.getenv("NEO4J_MYLOCAL_USERNAME")
        password = os.getenv("NEO4J_MYLOCAL_PASSWORD")

        if not all([url, username, password]):
            raise ValueError("Missing required environment variables")

        self.graph = Neo4jGraph(url=url, username=username, password=password)

        # Initialize the QA chain with the selected AI engine
        self.chain = GraphCypherQAChain.from_llm(
            self.ai_model, graph=self.graph, verbose=True, allow_dangerous_requests=True
        )

    def query(self, question: str):
        if not self.chain:
            raise ValueError("Chain not initialized. Check Neo4j connection.")

        return self.chain.run(question)
