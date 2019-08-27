import time


class Planning:
    def __init__(self, analysis):
        self.decision = 0
        self.analysis = analysis

    def get_decision(self):
        return self.decision

    def run_planning(self):
        self.decision = 0
        for result in self.analysis.get_result_list():
            if result == 1:
                self.decision += 1
            elif result == 2:
                self.decision -= 1

        if self.get_decision() > 0:
            print("Add {} containers".format(self.get_decision()))
        elif self.get_decision() < 0:
            print("Remove {} containers".format(- self.get_decision()))
        else:
            print("NTR")
        time.sleep(10)
