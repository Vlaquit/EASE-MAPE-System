import os
import time

import pymongo
import sys

from analysis.docker_threshold_analysis import ThresholdAnalysis
from execution.docker_execution import DockerExecution
from planning.threshold_planning import DockerPlanning


def main():
    analysis = ThresholdAnalysis(pymongo.MongoClient(os.getenv("URI")), 50, 30)
    planning = DockerPlanning(analysis)
    execution = DockerExecution(planning)

    analysis.attach(planning)
    planning.attach(execution)

    while True:
        analysis.update()
        time.sleep(10)


if __name__ == "__main__":
    main()
