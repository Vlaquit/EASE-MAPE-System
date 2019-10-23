from abc import ABC, abstractmethod


class Planning(ABC):
    def __init__(self):
        self.execution = None
        self.analysis = None

    def set_analysis(self, analysis):
        self.analysis = analysis

    def attach(self, execution):
        self.execution = execution

    def detach(self):
        self.execution = None

    def notify(self):
        self.execution.update()

    @abstractmethod
    def update(self):
        pass
