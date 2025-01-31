class ConnectorManager:
    def __init__(self):
        self.connectors = {}

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
