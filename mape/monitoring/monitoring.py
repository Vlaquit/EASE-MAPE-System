from abc import ABC


class Monitoring(ABC):
    def __init__(self, mongodb_client, env_client):
        self.mongodb_client = mongodb_client
        self.env_client = env_client

    def database_insertion(self, data):
        self.mongodb_client.monitoring.containers.insert_one(data)
