import datetime
import os
import sys
import time

import docker
import pymongo
import pytz
from dotenv import load_dotenv

from monitoring import Monitoring

load_dotenv()


class DockerMonitoring(Monitoring):
    def __init__(self, mongodb_client, env_client):
        super().__init__(mongodb_client, env_client)
        self.delay = 0.0
        self.nb_containers = 0
        self.cpu = 0.0
        self.system_cpu = 0.0
        self.previous_cpu = 0.0
        self.previous_system_cpu = 0.0
        self.cpu_percent = 0.0
        self.memory = 0.0
        self.memory_limit = 0.0
        self.memory_percent = 0.0
        self.disk_i = 0.0
        self.disk_o = 0.0
        self.rx_bytes = 0.0
        self.tx_bytes = 0.0

    def get_cpu_percent(self, data):
        if data['cpu_stats']['cpu_usage']['total_usage'] is not None:
            self.cpu = int(data['cpu_stats']['cpu_usage']['total_usage'])
        if data['cpu_stats']['system_cpu_usage'] is not None:
            self.system_cpu = int(data['cpu_stats']['system_cpu_usage'])
        if data['precpu_stats']['cpu_usage']['total_usage'] is not None:
            self.previous_cpu = int(data['precpu_stats']['cpu_usage']['total_usage'])
        if data['precpu_stats']['system_cpu_usage'] is not None:
            self.previous_system_cpu = int(data['precpu_stats']['system_cpu_usage'])
        if data['cpu_stats']['cpu_usage']['percpu_usage'] is not None:
            percpu_len = len(data['cpu_stats']['cpu_usage']['percpu_usage'])
        else:
            percpu_len = 1

        cpu_delta = self.cpu - self.previous_cpu
        system_delta = self.system_cpu - self.previous_system_cpu

        if system_delta > 0.0 and cpu_delta > 0.0:
            self.cpu_percent = (cpu_delta / system_delta) * percpu_len * 100

        return self.cpu_percent

    def get_memory(self, data):
        if data['memory_stats']['usage'] is not None:
            self.memory = int(data['memory_stats']['usage'])
        if data['memory_stats']['limit'] is not None:
            self.memory_limit = int(data['memory_stats']['limit'])
        return {'memory': self.memory, 'memory_limit': self.memory_limit, 'memory_percent': 100 * self.memory / self.memory_limit}

    def get_disk_io(self, data):
        if len(data['blkio_stats']['io_service_bytes_recursive']) >= 2:
            self.disk_i = int(data['blkio_stats']['io_service_bytes_recursive'][0]['value'])
        if len(data['blkio_stats']['io_service_bytes_recursive']) >= 2:
            self.disk_o = int(data['blkio_stats']['io_service_bytes_recursive'][1]['value'])

        return {'disk_i': self.disk_i, 'disk_o': self.disk_o}

    def get_network_throughput(self, data):
        if data['networks']['eth0']['rx_bytes'] is not None:
            self.rx_bytes = int(data['networks']['eth0']['rx_bytes'])
        if data['networks']['eth0']['tx_bytes'] is not None:
            self.tx_bytes = int(data['networks']['eth0']['tx_bytes'])

        return {'rx': self.rx_bytes, 'tx': self.tx_bytes}

    def update(self):
        t1 = time.time()
        print("Monitoring V2\nUsing: Docker remote API")
        self.delay = 0
        self.nb_containers = 0
        containers = self.env_client.containers.list()
        data = {'date': datetime.datetime.now(pytz.timezone('America/Montreal')), 'nb_containers': 0}
        for cont in containers:
            if "web" in str(cont.labels.get('com.docker.compose.service')):
                self.nb_containers += 1
                try:
                    container_stats = cont.stats(decode=False, stream=False)
                    name = cont.name.replace(".", "_")
                    data[name] = {'short_id': cont.short_id,
                                  'cpu_percent': self.get_cpu_percent(container_stats),
                                  'memory': self.get_memory(container_stats)['memory'],
                                  'memory_limit': self.get_memory(container_stats)['memory_limit'],
                                  'memory_percent': self.get_memory(container_stats)['memory_percent'],
                                  'disk_i': self.get_disk_io(container_stats)['disk_i'],
                                  'disk_o': self.get_disk_io(container_stats)['disk_o'],
                                  'net_rx': self.get_network_throughput(container_stats)['rx'],
                                  'net_tx': self.get_network_throughput(container_stats)['tx']}
                except:
                    pass
        data['nb_containers'] = self.nb_containers
        super().database_insertion(data)
        t2 = time.time()
        self.delay = float(t2 - t1)
        print("Time to insert into the database {:.2f} \n ______________".format(self.delay))


def main():
    monitoring = DockerMonitoring(pymongo.MongoClient(os.getenv("URI")), docker.from_env())
    while True:
        monitoring.update()


if __name__ == "__main__":
    main()
