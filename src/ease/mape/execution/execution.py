import os
import time
from abc import ABC, abstractmethod

from dotenv import load_dotenv

# Get environment variable
load_dotenv()


class Execution(ABC):
    def __init__(self):
        self.monitoring = None

    @abstractmethod
    def scale(self, planning):
        pass

    @abstractmethod
    def notify(self):
        pass

    @abstractmethod
    def attach(self, monitoring):
        pass


class DockerScale(Execution):

    def scale(self, planning):
        # self.notify()
        if planning.decision > 0:

            if planning.nb_containers >= 8:
                print("Maximum number of containers reached")
            else:
                os.system("docker-compose -f {} up -d --scale web={}".format(os.getenv("DOCKER_COMPOSE_FILE_DIRECTORY"),
                                                                             planning.nb_containers + 1))
        elif planning.decision < 0 and planning.nb_containers > 1:
            if planning.nb_containers + planning.decision < 1:
                os.system("docker-compose -f {} up -d --scale web={}".format(os.getenv("DOCKER_COMPOSE_FILE_DIRECTORY"), 1))
            else:
                os.system("docker-compose -f {} up -d --scale web={}".format(os.getenv("DOCKER_COMPOSE_FILE_DIRECTORY"),
                                                                             planning.nb_containers - 1))
        time.sleep(15)
        # self.notify()

    def notify(self):
        self.monitoring.make_break(self)

    def attach(self, monitoring):
        self.monitoring = monitoring
