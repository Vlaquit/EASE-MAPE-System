import sys

from numpy import mean
sys.path.insert(0, ".")

from analysis.analysis import Analysis


class ThresholdAnalysis(Analysis):
    def __init__(self, mongodb_client, upper_threshold, lower_threshold):
        if upper_threshold <= lower_threshold or upper_threshold >100 or lower_threshold <0:
            raise ValueError("Invalid threshold. Please make sure 0<lower_threshold<upper_threshold<100.")
        super().__init__(mongodb_client)

        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.nb_containers = 0
        self.result = 0
        self.cpu_list = []
        self.pre_cpu_average = 0
        self.cpu_average = 0

    def get_nb_containers(self):
        return self.nb_containers

    def get_result(self):
        return self.result

    def get_upper_threshold(self):
        return self.upper_threshold

    def get_lower_threshold(self):
        return self.lower_threshold

    def analyse_cpu(self, cpu_average):
        if cpu_average <= self.get_lower_threshold():
            return -1
        elif cpu_average >= self.get_upper_threshold():
            return 1
        else:
            return 0

    def update(self):
        last_data = super().get_last_data()
        self.nb_containers = last_data.get("nb_containers")
        self.cpu_list = []
        data_items = list(last_data.items())
        for i in range(3, len(data_items)):
            self.cpu_list.append(data_items[i][1].get("cpu_percent"))
        self.cpu_average = mean(self.cpu_list)
        print("CPU average {} ".format(self.cpu_average))
        print("Pre CPU average {} ".format(self.pre_cpu_average))
        print("Thresholds : Upper {} Lower {}".format(self.get_upper_threshold(),self.get_lower_threshold()))
        if self.pre_cpu_average != self.cpu_average:
            self.pre_cpu_average = self.cpu_average
            if self.analyse_cpu(self.cpu_average) == -1 :
                self.result = self.analyse_cpu(self.cpu_average)
                print("Analyse: Scale down\n")
                super().notify()
            elif self.analyse_cpu(self.cpu_average) == 1 :
                self.result = self.analyse_cpu(self.cpu_average)
                print("Analyse: Scale up\n")
                super().notify()
            else:
                print("Analyse: RAS\n")
        else:
            print("Analyse: RAS\n")

