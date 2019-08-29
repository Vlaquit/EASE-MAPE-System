import os
import time
from abc import ABC, abstractmethod
import docker


class Execution(ABC):
    def __init__(self, planning):
        self.planning = planning

    @abstractmethod
    def scale(self):
        pass


class DockerScale(Execution):

    def scale(self):
        if self.planning.get_decision() != 0:
            os.system("gnome-terminal && cd /home/valentin/Documents/Stage/iot-docker-mongoDB && docker-compose up -d --scale web=%d" % (self.planning.get_decision()))
            time.sleep(5)
