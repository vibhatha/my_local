class ConnectorManager:
    def __init__(self):
        self.connectors = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Close all registered connectors
        for connector in self.connectors.values():
            if hasattr(connector, "close"):
                connector.close()

    def register_connector(self, name, connector):
        self.connectors[name] = connector

    def get_connector(self, name):
        connector = self.connectors.get(name)
        if not connector:
            raise ValueError(f"Connector '{name}' not found.")
        return connector

    def get_connector_type(self, name):
        connector = self.get_connector(name)
        return type(connector)
