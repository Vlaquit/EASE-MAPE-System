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
        self.result_dict = {}
        self.result_dict_temp = {}

    def cpu_analyse(self, value):
        super().cpu_analyse(self)
        if value > float(os.getenv("CPU_UPPER_THRESHOLD")):
            return 1
        elif value < float(os.getenv("CPU_LOWER_THRESHOLD")):
            return 2
        else:
            return 0

    def get_result_dict(self):
        return self.result_dict

    def get_data_analysed(self):
        os.system("clear")
        super().get_data_analysed()
        last_data = self.db.containers.find_one(sort=[('_id', pymongo.DESCENDING)])
        data_items = list(last_data.items())
        self.result_dict_temp = {}
        for i in range(2, len(data_items) - 1):
            cont_name = str(data_items[i][0])
            self.result_dict_temp[cont_name] = {self.cpu_analyse(data_items[i][1].get("cpu").get("cpu_usage"))}
        self.result_dict = self.result_dict_temp
        print("________________")
        print("Analyse: Done !")


class LinearModelAnalysis(Analysis):
    def __init__(self):
        self.capacity = 2.5

    def get_requests(self):
        pass

    def set_capacity(self, cpu, precision, maximum):
        if maximum > 1 or maximum < 0:
            raise Exception("the maximum value must be between 0 and 1")
        self.capacity = 0
        for i in range(1, precision):
            self.capacity += self.get_requests() / cpu
        self.capacity = self.capacity * maximum / precision

    def cpu_analyse(self, value):
        pass

    def get_data_analysed(self):
        pass
