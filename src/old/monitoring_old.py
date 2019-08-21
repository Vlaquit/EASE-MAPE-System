import datetime
import os
import time

import docker
import pymongo
from dotenv import load_dotenv

# Get environment variable
load_dotenv()


# Gets the CPU data from dictionary, calculates the percentage and returns it
def get_cpu_percent(data):
    cpu_percent = None
    if data['cpu_stats']['cpu_usage']['total_usage'] is not None:
        cpu = int(data['cpu_stats']['cpu_usage']['total_usage'])
    else:
        cpu = 0
    if data['cpu_stats']['system_cpu_usage'] is not None:
        system_cpu = int(data['cpu_stats']['system_cpu_usage'])
    else:
        system_cpu = 0
    if data['precpu_stats']['cpu_usage']['total_usage'] is not None:
        previous_cpu = int(data['precpu_stats']['cpu_usage']['total_usage'])
    else:
        previous_cpu = 0
    if data['precpu_stats']['system_cpu_usage'] is not None:
        previous_system_cpu = int(data['precpu_stats']['system_cpu_usage'])
    else:
        previous_system_cpu = 0
    if data['cpu_stats']['cpu_usage']['percpu_usage'] is not None:
        percpu_len = len(data['cpu_stats']['cpu_usage']['percpu_usage'])
    else:
        percpu_len = 1

    cpu_delta = cpu - previous_cpu
    system_delta = system_cpu - previous_system_cpu

    if system_delta > 0.0 and cpu_delta > 0.0:
        cpu_percent = (cpu_delta / system_delta) * percpu_len * 100

    return cpu_percent


# Gets the memory data and returns the current memory usage, the limit of available memory and the percentage of memory usage
def get_memory(data):
    if data['memory_stats']['usage'] is not None:
        memory = int(data['memory_stats']['usage'])
    else:
        memory = None
    if data['memory_stats']['limit'] is not None:
        memory_limit = int(data['memory_stats']['limit'])
    else:
        memory_limit = None

    return {'memory': memory, 'memory_limit': memory_limit, 'memory_percent': 100 * memory / memory_limit}


# Gets the disk I/O and returns both
def get_disk_io(data):
    if len(data['blkio_stats']['io_service_bytes_recursive']) >= 2:
        disk_i = int(data['blkio_stats']['io_service_bytes_recursive'][0]['value'])
    else:
        disk_i = None
    if len(data['blkio_stats']['io_service_bytes_recursive']) >= 2:
        disk_o = int(data['blkio_stats']['io_service_bytes_recursive'][1]['value'])
    else:
        disk_o = None

    return {'disk_i': disk_i, 'disk_o': disk_o}


# Gets the rx and tx of the network and returns both
def get_network_throughput(data):
    if data['networks']['eth0']['rx_bytes'] is not None:
        rx_bytes = int(data['networks']['eth0']['rx_bytes'])
    else:
        rx_bytes = None
    if data['networks']['eth0']['tx_bytes'] is not None:
        tx_bytes = int(data['networks']['eth0']['tx_bytes'])
    else:
        tx_bytes = None

    return {'rx': rx_bytes, 'tx': tx_bytes}


def get_containers(docker_client):
    return docker_client.containers.list()


def run_monitoring():
    docker_client = docker.from_env()
    mongo_client = pymongo.MongoClient("mongodb://" + os.getenv("MONGODB_ID") + ":" + os.getenv("MONGODB_PW") + "@127.0.0.1")
    db = mongo_client.monitoring
    while True:
        os.system("clear")
        print("Monitoring is running")
        containers = get_containers(docker_client)
        data_dict = {'date': datetime.datetime.utcnow()}
        for cont in containers:
            cont_data_dict = cont.stats(decode=False, stream=False)
            data_dict[cont.name] = {'short_id': cont.short_id,
                                    'cpu': {'cpu_usage': get_cpu_percent(cont_data_dict)},
                                    'memory': {'memory': get_memory(cont_data_dict)['memory'],
                                               'memory_limit': get_memory(cont_data_dict)['memory_limit'],
                                               'memory_percent': get_memory(cont_data_dict)['memory_percent']},
                                    'disk': {'disk_i': get_disk_io(cont_data_dict)['disk_i'],
                                             'disk_o': get_disk_io(cont_data_dict)['disk_o']},
                                    'network': {'rx': get_network_throughput(cont_data_dict)['rx'],
                                                'tx': get_network_throughput(cont_data_dict)['tx']}}

        post = data_dict
        db.containers.insert_one(post).inserted_id
        print("The data is stored in the database")
        time.sleep(10)


# def main():
#     print("*** MONITORING ***")
#     print("Do you want to see stream of the monitoring ?")
#     answer = False
#     while answer is False:
#         x = input("y/n : ")
#         if x == "y":
#             answer = True
#             os.system("clear")
#             run_monitoring(True)
#         elif x == "n":
#             answer = True
#             os.system("clear")
#             run_monitoring(False)
#         else:
#             print("Please enter y for yes or n for no.")
#             time.sleep(1)


if __name__ == '__main__':
    run_monitoring()
