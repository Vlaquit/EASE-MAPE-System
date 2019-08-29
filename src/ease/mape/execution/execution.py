import os
import re
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

    def get_number_of_containers(self):
        num = 0
        pattern = re.compile(r".*_%s_\d+$" % "web")
        with os.popen("docker-compose -f /home/valentin/Documents/Stage/iot-docker-mongoDB ps") as f:
            for s in f.readlines():
                if "Up" in s:
                    ss = s.split()
                    if ss and pattern.match(ss[0]):
                        num += 1
        return num

    def scale(self):
        if self.planning.get_decision() > 0:
            if self.get_number_of_containers() >= 10:
                print("Maximum number of containers reached")
            else:
                os.system("docker-compose -f /home/valentin/Documents/Stage/iot-docker-mongoDB/docker-compose.yml up -d --scale web=%d" % (self.planning.get_decision()))
        # elif self.planning.get_decision() < 0 and self.get_number_of_containers()+self.planning.get_decision() >= 1:
        #    os.system("docker-compose -f /home/valentin/Documents/Stage/iot-docker-mongoDB/docker-compose.yml up -d --scale web=%d" % (self.get_number_of_containers()+self.planning.get_decision()))

        time.sleep(5)
