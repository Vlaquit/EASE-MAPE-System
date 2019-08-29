import pymongo
import sys


sys.path.insert(0, "/home/valentin/Documents/Stage/EASE MAPE System/src")

from ease.mape.analysis.analysis import ThresholdAnalysis
from ease.mape.planning.planning import Planning
from ease.mape.execution.execution import DockerScale


def main():
    analyse = ThresholdAnalysis(pymongo.MongoClient("mongodb://root:password@localhost:27017/"))
    plan = Planning(analyse)
    execution = DockerScale(plan)
    while True:
        analyse.get_data_analysed()
        plan.run_planning()
        execution.scale()


if __name__ == "__main__":
    main()
