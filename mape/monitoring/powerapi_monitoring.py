#TODO
import datetime
import os
import sys
from time import time, sleep

import docker
import pymongo
import pytz
from dotenv import load_dotenv

from monitoring import Monitoring

load_dotenv()


class PowerapiMonitoring(Monitoring):
    def __init__(self, mongodb_client, env_client):
        super().__init__(mongodb_client, env_client)
        self.delay = 0
        self.nb_containers= 0

    def get_measurements(self):
        t1 = time()
        print("Monitoring\nUsing: PowerAPI")
        containers = self.env_client.containers.list()
        data = {'date': datetime.datetime.now(pytz.timezone('America/Montreal')), 'nb_containers': 0}
        self.nb_containers = 0

        for cont in containers:
            if "web" in str(cont.labels.get('com.docker.compose.service')):
                self.nb_containers += 1
                name = cont.name.replace(".", "_")
                try:
                    data[name] = {'cpu_power': float(self.mongodb_client.powerapi.formula.find_one({"target": cont.name}, sort=[('_id', pymongo.DESCENDING)]).get("power"))}
                except:
                    pass

        data['nb_containers'] = self.nb_containers
        super().database_insertion(data, "power")

        t2 = time()
        self.delay = float(t2 - t1)
        print("Size of data = {} bytes".format(sys.getsizeof(data)))
        print("Time to insert into the database {:.2f} sec\n ______________".format(self.delay))

def main():
    monitoring = PowerapiMonitoring(pymongo.MongoClient(os.getenv("URI")), docker.from_env())
    while True:
        monitoring.get_measurements()
        sleep(3)


if __name__ == "__main__":
    main()