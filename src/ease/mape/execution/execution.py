import os
import re
import sys
import time
from abc import ABC, abstractmethod
import docker

from ease.mape.monitoring import monitoring


class Execution(ABC):
    def __init__(self, planning):
        self.planning = planning

    @abstractmethod
    def scale(self):
        pass


class DockerScale(Execution):

    def scale(self):
        if self.planning.get_decision() > 0:
            if self.planning.get_number_of_containers() >= 15:
                print("Maximum number of containers reached")
            else:
                os.system("docker-compose -f /home/valentin/Documents/Stage/iot-docker-mongoDB/docker-compose.yml up -d --scale web=%d" % (
                        self.planning.get_number_of_containers() + self.planning.get_decision()))
        elif self.planning.get_decision() < 0:
            if self.planning.get_number_of_containers() + self.planning.get_decision() < 1:
                os.system("docker-compose -f /home/valentin/Documents/Stage/iot-docker-mongoDB/docker-compose.yml up -d --scale web=%d" % 1)
            else:
                os.system("docker-compose -f /home/valentin/Documents/Stage/iot-docker-mongoDB/docker-compose.yml up -d --scale web=%d" % (
                        self.planning.get_number_of_containers() + self.planning.get_decision()))
        time.sleep(15)
