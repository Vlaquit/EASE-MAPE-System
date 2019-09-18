import os

import pymongo
import sys

sys.path.insert(0, "/home/valentin/Documents/Stage/EASE MAPE System/src")

from ease.mape.analysis.threshold_analysis import DockerThresholdAnalysis
from ease.mape.planning.planning import DockerPlanning
from ease.mape.execution.execution import DockerScale


def main():
    analyse = DockerThresholdAnalysis(pymongo.MongoClient(os.getenv("URI")))
    plan = DockerPlanning()
    execution = DockerScale()
    analyse.attach(plan)
    plan.attach(execution)

    while True:
        analyse.run_analysis()


if __name__ == "__main__":
    main()
