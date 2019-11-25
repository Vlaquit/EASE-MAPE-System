from abc import ABC, abstractmethod


class Monitoring(ABC):
    def __init__(self, mongodb_client, env_client):
        self.mongodb_client = mongodb_client
        self.env_client = env_client

    def database_insertion(self, data, col):
        if col == "containers":
            self.mongodb_client.monitoring.containers.insert_one(data)
        elif col == "power":
            self.mongodb_client.monitoring.power.insert_one(data)
    @abstractmethod
    def get_measurements(self):
        pass