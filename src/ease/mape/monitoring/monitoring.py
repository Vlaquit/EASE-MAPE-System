import datetime
import os
import time
from abc import ABC, abstractmethod

import docker
import pymongo
import csv

import pytz
from numpy import mean


from dotenv import load_dotenv

# Get environment variable
load_dotenv()


class Monitoring(ABC):
    def __init__(self, client_to_monitor, mongo_client):
        self.client_to_monitor = client_to_monitor
        self.mongo_client = mongo_client
        self.db = None
        self.run = True
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
        # self.db.containers.drop()

    @abstractmethod
    def make_break(self):
        pass


class DockerMonitoring(Monitoring):
    def __init__(self, client_to_monitor, mongo_client):
        super().__init__(client_to_monitor, mongo_client)
        self.nb_containers = 0
        self.csv_file = None

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

    def make_break(self):
        self.run = not self.run

    def export_to_csv(self, csv_file, data):
        data['date'] = data['date'].strftime('%B %d %Y - %H:%M:%S')

        pass

    def run_monitoring(self):

        self.nb_containers = 0
        self.delay = 0.0
        os.system("clear")
        print("Monitoring is running\n")

        t1 = time.time()

        containers = self.client_to_monitor.containers.list()
        if self.run:

            container_data = {'date': datetime.datetime.now(pytz.timezone('America/Montreal')), 'nb_of_containers': 0}

            list_cpu = []
            list_mem = []
            list_disk_i = []
            list_disk_o = []
            for cont in containers:
                if "db" not in str(cont.labels.get('com.docker.compose.service')):
                    self.nb_containers += 1
                    try:
                        container_stats = cont.stats(decode=False, stream=False)
                        name = cont.name.replace(".", "_")
                        container_data[name] = {'short_id': cont.short_id,
                                                     'cpu': {'cpu_usage': self.get_cpu_percent(container_stats)},
                                                     'memory': {'memory': self.get_memory(container_stats)['memory'],
                                                                'memory_limit': self.get_memory(container_stats)['memory_limit'],
                                                                'memory_percent': self.get_memory(container_stats)['memory_percent']},
                                                     'disk': {'disk_i': self.get_disk_io(container_stats)['disk_i'],
                                                              'disk_o': self.get_disk_io(container_stats)['disk_o']},
                                                     'network': {'rx': self.get_network_throughput(container_stats)['rx'],
                                                                 'tx': self.get_network_throughput(container_stats)['tx']}}

                        list_cpu.append(container_data[name].get("cpu").get("cpu_usage"))
                        list_mem.append(container_data[name]['memory']['memory_percent'])
                        list_disk_i.append(container_data[name]['disk']['disk_i'])
                        list_disk_o.append(container_data[name]['disk']['disk_o'])

                    except:
                        pass

            cpu_average = round(mean(list_cpu), 2)
            mem_average = round(mean(list_mem), 2)
            disk_i_average = round(mean(list_disk_i), 2)
            disk_o_average = round(mean(list_disk_o), 2)

            with open('csv_file.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([container_data['date'].strftime('%H:%M:%S'),
                                 cpu_average,
                                 mem_average,
                                 disk_i_average,
                                 disk_o_average,
                                 self.nb_containers
                                 ])
            container_data['nb_of_containers'] = self.nb_containers

            self.db.containers.insert_one(container_data)

            t2 = time.time()
            self.delay = float(t2 - t1)

            print("Containers data stored in {:.2f} sec\n".format(self.delay))
            print("---- Sleep 5 sec ----")
            time.sleep(10)
        else:
            print("Wait for execution done")
            time.sleep(15)

    def main(self):
        super().run_monitoring()
        with open('csv_file.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "cpu %", "memory %", "disk I", "disk O", "number"])
        while True:
            self.run_monitoring()


# TODO
class KubernetesMonitoring(Monitoring):

    def get_cpu_percent(self, data):
        pass

    def make_break(self):
        pass

    def get_memory(self, data):
        pass

    def get_disk_io(self, data):
        pass

    def get_network_throughput(self, data):
        pass

    def run_monitoring(self):
        pass


if __name__ == "__main__":
    docker_monitoring = DockerMonitoring(docker.from_env(), pymongo.MongoClient(os.getenv("URI")))
    docker_monitoring.main()
