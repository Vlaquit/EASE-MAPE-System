from abc import ABC, abstractmethod

import pymongo
from dotenv import load_dotenv

load_dotenv()

class Analysis(ABC):
    def __init__(self, mongodb_client):
        self.mongodb_client = mongodb_client
        self.planning = None

    def get_last_data(self):
        return self.mongodb_client.monitoring.containers.find_one(sort=[('_id', pymongo.DESCENDING)])

    def attach(self, planning):
        self.planning = planning

    def detach(self):
        self.planning = None

    def notify(self):
        self.planning.update()

    @abstractmethod
    def update(self):
        pass