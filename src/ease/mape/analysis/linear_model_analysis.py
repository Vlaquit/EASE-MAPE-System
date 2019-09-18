from abc import ABC, abstractmethod


class LinearModelAnalysis(ABC):
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.db = None
        self.capacity = 0

    def get_capacity(self):
        return self.capacity

    @abstractmethod
    def get_requests(self):
        pass

    @abstractmethod
    def set_capacity(self, precision, maximum):
        pass

    @abstractmethod
    def run_analysis(self):
        pass


class DockerLinearModelAnalysis(LinearModelAnalysis):
    def get_requests(self):
        pass

    def set_capacity(self, precision, maximum):
        if maximum > 1 or maximum < 0:
            raise Exception("the maximum value must be between 0 and 1")
        self.capacity = 0
        for i in range(1, precision):
            self.capacity += self.get_requests() / self.get_cpu()
        self.capacity = self.capacity * maximum / precision

    def run_analysis(self):
        pass

    def get_cpu(self):
        pass
