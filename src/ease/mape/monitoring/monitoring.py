import csv
import datetime
import io
import json
import os
import sys
import time
from abc import ABC, abstractmethod
from ast import literal_eval

sys.path.insert(0, "./src")


import docker
import pymongo
import pytz
import requests
from dotenv import load_dotenv
from numpy import mean

# Get environment variable
from ease.mape.monitoring import haproxy_monitoring

load_dotenv()


class Monitoring(ABC):
    def __init__(self, client_to_monitor, mongo_client):
        self.client_to_monitor = client_to_monitor
        self.mongo_client = mongo_client
        self.db = None

    @abstractmethod
    def run_monitoring(self):
        self.db = self.mongo_client.monitoring
        # self.db.containers.drop()


class DockerMonitoringV1(Monitoring):
    def __init__(self, client_to_monitor, mongo_client):
        super().__init__(client_to_monitor, mongo_client)
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
        self.nb_containers = 0
        self.haproxy_stats = []
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

    def run_monitoring(self):

        self.nb_containers = 0
        self.delay = 0.0
        os.system("clear")
        print("Monitoring is running\nDocker remote API")

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

            try:
                self.haproxy_stats = haproxy_monitoring.get_data(haproxy_monitoring.get_haproxy_stats(os.getenv("HAPROXY_URL")))
            except:
                pass

            with open('csv_file.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([container_data['date'].strftime('%H:%M:%S'),
                                 cpu_average,
                                 mem_average,
                                 disk_i_average,
                                 disk_o_average,
                                 self.nb_containers,
                                 self.haproxy_stats[0],
                                 self.haproxy_stats[1],
                                 self.haproxy_stats[2]
                                 ])
            container_data['nb_of_containers'] = self.nb_containers

            self.db.containers.insert_one(container_data)

            t2 = time.time()
            self.delay = float(t2 - t1)
            print("Time to insert into the database {:.2f}".format(self.delay))
            print(type(os.getenv("SLEEP_TIME")))
            print(type(self.delay))

            if self.delay < int(os.getenv("SLEEP_TIME")):
                t3 = time.time()
                time.sleep(int(os.getenv("SLEEP_TIME")) - self.delay)
                t4 = time.time()
                self.delay = t4 - t1

            print("Done in {:.2f} sec\n".format(self.delay))
            # wait = 10
            # print("---- Sleep % sec ----" % wait)
            # time.sleep(wait)
        else:
            print("Wait for execution done")
            time.sleep(int(os.getenv("SLEEP_TIME")))

    def main(self):
        super().run_monitoring()
        with open('csv_file.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "cpu %", "memory %", "disk I", "disk O", "number", "haproxy_resp_time", "haproxy_session_rate", "haproxy_nb_sessions"])
        while True:
            self.run_monitoring()


class DockerMonitoringV2(Monitoring):

    def run_monitoring(self):
        pass


# TODO
class KubernetesMonitoring(Monitoring):

    def run_monitoring(self):
        pass


class CAdvisorMonitoring(Monitoring):
    def __init__(self, mongo_client, cadvisor_host):
        super().__init__(mongo_client, cadvisor_host)
        self.cpu_data = {}
        self.data = {}
        self.nb_containers = 0
        self.delay = 0.0

    def get_cadvisor_stats(self, url):
        req = requests.get(url)
        page = req.content
        data = page.decode("utf8")
        # print(data)
        reader = csv.DictReader(io.StringIO(data))
        json_data = json.dumps(list(page))
        # print(json_data)
        return data

    def run_monitoring(self):
        super().run_monitoring()
        os.system("clear")
        print("Monitoring is running\ncAdvisor")
        containers = docker.from_env().containers.list()
        self.data = {}
        self.cpu_data = {}
        for cont in containers:
            cont_short_id = str(cont.short_id)
            cont_id = str(cont.id)
            cont_name = str(cont.name).replace(".", "_")
            cont_service = cont.labels.get('com.docker.compose.service')

            url = self.client_to_monitor + cont_short_id
            self.data[cont_name] = json.loads(self.get_cadvisor_stats(url))
            self.cpu_data[cont_name] = {"service": cont_service, "cpu_total_usage": self.data[cont_name]["/docker/" + cont_id]["stats"][-1]["cpu"]["usage"]["total"]}
        print(self.cpu_data)
        self.db.cadvisor_monitoring.insert_one(self.cpu_data)
        print("successful")


if __name__ == "__main__":
    docker_monitoring = DockerMonitoringV1(docker.from_env(), pymongo.MongoClient(os.getenv("URI")))
    docker_monitoring.main()
    # cadvisor_monitoring = CAdvisorMonitoring("http://localhost:8080/api/v1.3/docker/", pymongo.MongoClient(os.getenv("URI")))
    # cadvisor_monitoring.run_monitoring()
