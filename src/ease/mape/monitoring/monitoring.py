import datetime
import os
import time
from abc import ABC, abstractmethod

import docker
import pymongo
from dotenv import load_dotenv

# Get environment variable
load_dotenv()


class Monitoring(ABC):
    def __init__(self, client_to_monitor, mongo_client):
        self.client_to_monitor = client_to_monitor
        self.mongo_client = mongo_client
        self.db = None
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
        self.delay = 0.0

    @abstractmethod
    def get_cpu_percent(self, data):
        pass

    @abstractmethod
    def get_memory(self, data):
        pass

    @abstractmethod
    def get_disk_io(self, data):
        pass

    @abstractmethod
    def get_network_throughput(self, data):
        pass

    @abstractmethod
    def run_monitoring(self):
        self.db = self.mongo_client.monitoring


class DockerMonitoring(Monitoring):

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

    def run_monitoring(self):
        super().run_monitoring()
        while True:
            os.system("clear")
            print("Monitoring is running\n")
            self.delay = 0.0
            t1 = time.time()
            containers = self.client_to_monitor.containers.list()
            data_dict = {'date': datetime.datetime.utcnow()}
            for cont in containers:
                cont_data_dict = cont.stats(decode=False, stream=False)
                data_dict[cont.name] = {'short_id': cont.short_id,
                                        'cpu': {'cpu_usage': self.get_cpu_percent(cont_data_dict)},
                                        'memory': {'memory': self.get_memory(cont_data_dict)['memory'],
                                                   'memory_limit': self.get_memory(cont_data_dict)['memory_limit'],
                                                   'memory_percent': self.get_memory(cont_data_dict)['memory_percent']},
                                        'disk': {'disk_i': self.get_disk_io(cont_data_dict)['disk_i'],
                                                 'disk_o': self.get_disk_io(cont_data_dict)['disk_o']},
                                        'network': {'rx': self.get_network_throughput(cont_data_dict)['rx'],
                                                    'tx': self.get_network_throughput(cont_data_dict)['tx']}}

            self.db.containers.insert(data_dict)
            t2 = time.time()
            self.delay = t2 - t1
            print(self.delay)
            print("Containers data stored\n---- Sleep 10 sec ----")
            time.sleep(10)


x = DockerMonitoring(docker.from_env(), pymongo.MongoClient("mongodb://root:password@localhost:27017/"))

x.run_monitoring()


class KubernetesMonitoring(Monitoring):

    def get_cpu_percent(self, data):
        pass

    def get_memory(self, data):
        pass

    def get_disk_io(self, data):
        pass

    def get_network_throughput(self, data):
        pass

    def run_monitoring(self):
        pass
