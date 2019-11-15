import sys

sys.path.insert(0, ".")

from planning.planning import Planning


class DockerPlanning(Planning):
    def __init__(self, analysis):
        super().__init__()
        super().set_analysis(analysis)
        self.decision = None
        # self.nb_containers = 0

    def get_decision(self):
        return self.decision

    def update(self):
        # self.nb_containers = self.analysis.get_nb_containers()
        self.decision = self.analysis.nb_containers + self.analysis.get_result()
        if self.decision < 1:
            self.decision = 1
        print("Plan\n")
        self.notify()
