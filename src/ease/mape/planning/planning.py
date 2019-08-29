import time
from abc import ABC, abstractmethod


class Planning(ABC):
    def __init__(self, analysis):
        self.decision = 0
        self.analysis = analysis

    def get_decision(self):
        return self.decision

    @abstractmethod
    def run_planning(self):
        pass


class DockerPlanning(Planning):
    def __init__(self, analysis):
        super().__init__(analysis)
        self.containters_to_scale = []

    def get_container_to_scale(self):
        return self.containters_to_scale

    def run_planning(self):
        self.decision = 0
        for key, value in self.analysis.get_result_dict().items():
            for val in value:
                value = val
            if value == 1:
                self.decision += 1
                self.containters_to_scale.append(key)
            elif value == 2:
                self.decision -= 1
                self.containters_to_scale.append(key)
        if self.get_decision() > 0:
            # print("Add {} containers".format(self.get_decision()))
            print("scale up")
        elif self.get_decision() < 0:
            # print("Remove {} containers".format(- self.get_decision()))
            print("scale down")
        else:
            print("NTR")
        time.sleep(5)
