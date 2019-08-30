import sys

import docker
import pymongo

sys.path.insert(0, "/home/valentin/Documents/Stage/EASE MAPE System/src")

from ease.mape.monitoring.monitoring import DockerMonitoring

x = DockerMonitoring(docker.from_env(), pymongo.MongoClient("mongodb://root:password@localhost:27017/"))

x.run_monitoring()
