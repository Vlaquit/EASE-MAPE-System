from abc import abstractmethod, ABC


class Execution(ABC):
    def __init__(self):
        self.planning = None

    def set_planning(self, planning):
        self.planning = planning

    @abstractmethod
    def update(self):
        pass
