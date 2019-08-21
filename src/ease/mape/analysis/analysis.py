import os
import time

import pymongo

from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Get environment variable
load_dotenv()


class Analysis(ABC):
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client

    @abstractmethod
    def cpu_analyse(self, value):
        pass

    def get_data_analysed(self):
        db = self.mongo_client.monitoring
        while True:
            last_data = db.containers.find_one(sort=[('_id', pymongo.DESCENDING)])
            data_items = list(last_data.items())
            for i in range(2, len(data_items)):
                print("Container n° : {}/{}".format(i - 1, len(data_items) - 2))
                print("CPU %: {:5.2f}".format(data_items[i][1].get("cpu").get("cpu_usage")))
                print("Result: {} \n".format(self.cpu_analyse(data_items[i][1].get("cpu").get("cpu_usage"))))
            print("________________")

            time.sleep(10)


class ThresholdAnalysis(Analysis):
    def cpu_analyse(self, value):
        super().cpu_analyse(self)
        if value > float(os.getenv("CPU_UPPER_THRESHOLD")):
            return 1
        elif value < float(os.getenv("CPU_LOWER_THRESHOLD")):
            return 2
        else:
            return 0


x = ThresholdAnalysis(pymongo.MongoClient("mongodb://" + os.getenv("MONGODB_ID") + ":" + os.getenv("MONGODB_PW") + "@127.0.0.1"))
x.get_data_analysed()


class ModelAnalysis(Analysis):
    def cpu_analyse(self, value):
        pass
