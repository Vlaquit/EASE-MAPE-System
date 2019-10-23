from abc import ABC, abstractmethod


class Planning(ABC):
    def __init__(self ):
        self.decision = 0
        self.execution = None

    @abstractmethod
    def update(self, analysis):
        pass

    @abstractmethod
    def notify(self):
        pass

    @abstractmethod
    def attach(self, execution):
        pass


class DockerPlanning(Planning):
    def __init__(self):
        super().__init__()
        self.nb_containers = 0

    def attach(self, execution):
        self.execution = execution

    def notify(self):
        self.execution.scale(self)

    def update(self, analysis):
        self.nb_containers = analysis.get_nb_containers()
        if analysis.result == 1:
            self.decision = 1
            self.prompt()
            self.notify()
        elif analysis.result == 2:
            self.decision = -1
            self.prompt()
            self.notify()
        else:
            self.decision = 0

    def prompt(self):
        if self.decision > 0:
            print("Current number of containers : %d" % self.nb_containers)
            print("Scale up to {} containers ".format(self.nb_containers + 1))
        elif self.decision < 0:
            print("Current number of containers : %d" % self.nb_containers)
            if self.nb_containers - 1 <= 1:
                print("Scale down to 1 containers ")
            else:
                print("Scale down to {} containers ".format(self.nb_containers - 1))
