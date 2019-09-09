import os
from abc import ABC, abstractmethod

import pymongo
from dotenv import load_dotenv

# Get environment variable
load_dotenv()


def cpu_analyse(value):
    if value > float(os.getenv("CPU_UPPER_THRESHOLD")):
        return 1
    elif value < float(os.getenv("CPU_LOWER_THRESHOLD")):
        return 2
    else:
        return 0


class ThresholdAnalysis(ABC):
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.db = None

    @abstractmethod
    def run_analysis(self):
        os.system("clear")
        self.db = self.mongo_client.monitoring


class DockerThresholdAnalysis(ThresholdAnalysis):
    def __init__(self, mongo_client):
        super().__init__(mongo_client)
        self.result_list = []
        self.result_list_temp = []
        self.nb_containers = 0

    def get_result_list(self):
        return self.result_list

    def get_nb_containers(self):
        return self.nb_containers

    def run_analysis(self):
        super().run_analysis()
        print("THRESHOLD ANALYSIS ...")
        last_data = self.db.containers.find_one(sort=[('_id', pymongo.DESCENDING)])
        data_items = list(last_data.items())
        self.nb_containers = data_items[2][1]
        self.result_list_temp = []
        for i in range(3, len(data_items)):
            self.result_list_temp.append(cpu_analyse(data_items[i][1].get("cpu").get("cpu_usage")))
        if self.result_list_temp == self.result_list:
            self.result_list = [-1]
        else:
            self.result_list = self.result_list_temp
        print("Done")
        print("CPU threshold :\n"
              "Upper = {}\n"
              "Lower = {}\n".format(os.getenv("CPU_UPPER_THRESHOLD"), os.getenv("CPU_LOWER_THRESHOLD")))
