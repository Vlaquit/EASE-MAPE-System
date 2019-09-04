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
        self.number_of_containers = 0

    def get_number_of_containers(self):
        return self.number_of_containers

    def get_container_to_scale(self):
        return self.containters_to_scale

    def run_planning(self):
        self.decision = 0
        self.number_of_containers = 0
        for key, value in self.analysis.get_result_dict().items():
            for val in value:
                value = val
            if "web" in key:
                self.number_of_containers += 1
            if value == 1 and "web" in key:
                self.decision += 1
                self.containters_to_scale.append(key)
            elif value == 2 and "web" in key:
                self.decision -= 1
                self.containters_to_scale.append(key)

        if self.get_decision() > 0:
            print("Current number of containers : %d" % self.get_number_of_containers())
            print("scale up to {} containers ".format(self.get_number_of_containers() + 1))
        elif self.get_decision() < 0:
            print("Current number of containers : %d" % self.get_number_of_containers())
            print("scale down to {} containers ".format(self.get_number_of_containers() - 1))
        else:
            print("Current number of containers : %d" % self.get_number_of_containers())
            print("NTR")
