import os
import time
from abc import ABC, abstractmethod

from dotenv import load_dotenv

# Get environment variable
load_dotenv()


class Execution(ABC):
    def __init__(self, planning):
        self.planning = planning

    @abstractmethod
    def scale(self):
        pass


class DockerScale(Execution):

    def scale(self):
        if self.planning.get_decision() > 0:
            if self.planning.get_nb_containers() >= 15:
                print("Maximum number of containers reached")
            else:
                os.system("docker-compose -f {} up -d --scale web={}".format(os.getenv("DOCKER_COMPOSE_FILE_DIRECTORY"),
                                                                             self.planning.get_nb_containers() + 1))
        elif self.planning.get_decision() < 0 and self.planning.get_nb_containers() > 1:
            if self.planning.get_nb_containers() + self.planning.get_decision() < 1:
                os.system("docker-compose -f {} up -d --scale web={}".format(os.getenv("DOCKER_COMPOSE_FILE_DIRECTORY"), 1))
            else:
                os.system("docker-compose -f {} up -d --scale web={}".format(os.getenv("DOCKER_COMPOSE_FILE_DIRECTORY"),
                                                                             self.planning.get_nb_containers() - 1))
        time.sleep(15)
