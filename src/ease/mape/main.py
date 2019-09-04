import pymongo
import sys

sys.path.insert(0, "/home/valentin/Documents/Stage/EASE MAPE System/src")

from ease.mape.analysis.threshold_analysis import DockerThresholdAnalysis
from ease.mape.planning.planning import DockerPlanning
from ease.mape.execution.execution import DockerScale


def main():
    analyse = DockerThresholdAnalysis(pymongo.MongoClient("mongodb://root:password@localhost:27017/"))
    plan = DockerPlanning(analyse)
    execute = DockerScale(plan)
    while True:
        analyse.run_analysis()
        plan.run_planning()
        execute.scale()


if __name__ == "__main__":
    main()
