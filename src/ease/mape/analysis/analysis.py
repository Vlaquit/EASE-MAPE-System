import os
from abc import ABC, abstractmethod

import pymongo
from dotenv import load_dotenv

# Get environment variable
load_dotenv()


class Analysis(ABC):
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.db = None

    @abstractmethod
    def cpu_analyse(self, value):
        pass

    @abstractmethod
    def get_data_analysed(self):
        self.db = self.mongo_client.monitoring


class ThresholdAnalysis(Analysis):
    def __init__(self, mongo_client):
        super().__init__(mongo_client)
        self.result_list = []
        self.result_list_temp = []

    def cpu_analyse(self, value):
        super().cpu_analyse(self)
        if value > float(os.getenv("CPU_UPPER_THRESHOLD")):
            return 1
        elif value < float(os.getenv("CPU_LOWER_THRESHOLD")):
            return 2
        else:
            return 0

    def get_result_list(self):
        return self.result_list

    def get_data_analysed(self):
        super().get_data_analysed()
        last_data = self.db.containers.find_one(sort=[('_id', pymongo.DESCENDING)])
        data_items = list(last_data.items())
        self.result_list_temp.clear()
        for i in range(2, len(data_items)):
            # print("Container n° : {}/{}".format(i - 1, len(data_items) - 2))
            # print("CPU %: {:5.2f}".format(data_items[i][1].get("cpu").get("cpu_usage")))
            # print("Result: {} \n".format(self.cpu_analyse(data_items[i][1].get("cpu").get("cpu_usage"))))
            self.result_list_temp.append(self.cpu_analyse(data_items[i][1].get("cpu").get("cpu_usage")))
        self.result_list = self.result_list_temp
        print("________________")
        print("Analyse: Done !")


#
# x = ThresholdAnalysis(pymongo.MongoClient("mongodb://root:password@localhost:27017/"))
# x.get_data_analysed()


class LinearModelAnalysis(Analysis):
    def cpu_analyse(self, value):
        pass

    def get_data_analysed(self):
        pass
