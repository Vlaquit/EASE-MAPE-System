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

    def get_nb_containers(self):
        return self.analysis.get_nb_containers()

    def run_planning(self):
        self.decision = 0
        for value in self.analysis.get_result_list():
            if value == 1:
                self.decision += 1
            elif value == 2:
                self.decision -= 1

        if self.get_decision() > 0:
            print("Current number of containers : %d" % self.get_nb_containers())
            print("Scale up to {} containers ".format(self.get_nb_containers() + 1))
        elif self.get_decision() < 0:
            print("Current number of containers : %d" % self.get_nb_containers())
            if self.get_nb_containers() - 1 < 1:
                print("Scale down to 1 containers ")
            else:
                print("Scale down to {} containers ".format(self.get_nb_containers() - 1))

        else:
            print("Current number of containers : %d" % self.get_nb_containers())
            print("NTR")
