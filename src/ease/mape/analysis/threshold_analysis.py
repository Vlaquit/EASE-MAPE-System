import os
import time
from abc import ABC, abstractmethod

import pymongo
from dotenv import load_dotenv
from numpy import mean

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
        self.planning = None
        self.db = None

    @abstractmethod
    def notify(self):
        pass

    @abstractmethod
    def attach(self, planning):
        pass

    @abstractmethod
    def run_analysis(self):
        os.system("clear")
        self.db = self.mongo_client.monitoring


class DockerThresholdAnalysis(ThresholdAnalysis):
    def __init__(self, mongo_client):
        super().__init__(mongo_client)
        self.cpu_average = 0
        self.result = 0
        self.cpu_list = []
        self.nb_containers = 0

    def attach(self, planning):
        self.planning = planning

    def notify(self):
        self.planning.update(self)

    def get_cpu_average(self):
        return self.cpu_average

    def get_nb_containers(self):
        return self.nb_containers

    def get_result(self):
        return self.result

    def run_analysis(self):
        super().run_analysis()
        print("THRESHOLD ANALYSIS ...")
        last_data = self.db.containers.find_one(sort=[('_id', pymongo.DESCENDING)])
        data_items = list(last_data.items())
        self.nb_containers = data_items[2][1]
        self.cpu_list = []
        for i in range(3, len(data_items)):
            self.cpu_list.append(data_items[i][1].get("cpu").get("cpu_usage"))
        self.cpu_average = mean(self.cpu_list)
        print("CPU average {} ".format(self.cpu_average))
        if self.result != cpu_analyse(self.cpu_average):
            self.result = cpu_analyse(self.cpu_average)
            self.notify()

        print("Done")

        time.sleep(5)

