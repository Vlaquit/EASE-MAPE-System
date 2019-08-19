import os
import time
import json
import pymongo
import datetime
import docker


def cpu_usage(data):
    cpu_percent = 0.0
    cpu = int(data['cpu_stats']['cpu_usage']['total_usage'])
    system_cpu = int(data['cpu_stats']['system_cpu_usage'])
    previous_cpu = int(data['precpu_stats']['cpu_usage']['total_usage'])
    previous_system_cpu = int(data['precpu_stats']['system_cpu_usage'])
    percpu_len = len(data['cpu_stats']['cpu_usage']['percpu_usage'])

    cpu_delta = cpu - previous_cpu
    system_delta = system_cpu - previous_system_cpu

    if system_delta > 0.0 and cpu_delta > 0.0:
        cpu_percent = (cpu_delta / system_delta) * percpu_len * 100

    return cpu_percent


def memory_usage(data):
    memory = int(data['memory_stats']['usage'])
    memory_limit = int(data['memory_stats']['limit'])

    return {'memory': memory, 'memory_limit': memory_limit, 'memory_percent': 100 * memory / memory_limit}


def disk_io(data):
    disk_i = int(data['blkio_stats']['io_service_bytes_recursive'][0]['value'])
    disk_o = int(data['blkio_stats']['io_service_bytes_recursive'][1]['value'])

    return {'disk_i': disk_i, 'disk_o': disk_o}


def network_throughput(data):
    rx_bytes = int(data['networks']['eth0']['rx_bytes'])
    tx_bytes = int(data['networks']['eth0']['tx_bytes'])

    return {'rx': rx_bytes, 'tx': tx_bytes}


docker_client = docker.from_env()
client = pymongo.MongoClient("mongodb+srv://Vlaquit:FsKxF8LT9Aqr6VKZ@cluster0-wuhr3.mongodb.net/test?retryWrites=true&w=majority")
db = client.monitoring

exiting = False


def run_monitoring(stream):
    streaming = stream
    while not exiting:
        containers = docker_client.containers.list()
        data_dict = {'date': datetime.datetime.utcnow()}
        data_json = None
        if streaming:
            os.system("clear")
            print("*** MONITORING STREAM ***")
            # print("==> Docker hostname : {}".format(containers.hostname))
            print("==> Number of containers : {}".format(len(containers)))
            print("______________________________________________________")
            for cont in containers:
                cont_data_dict = cont.stats(decode=False, stream=False)

                data_dict[cont.name] = {'short_id': cont.short_id,
                                        'cpu': {'cpu_usage': cpu_usage(cont_data_dict)},
                                        'memory': {'memory': memory_usage(cont_data_dict)['memory'],
                                                   'memory_limit': memory_usage(cont_data_dict)['memory_limit'],
                                                   'memory_percent': memory_usage(cont_data_dict)['memory_percent']},
                                        'disk': {'disk_i': disk_io(cont_data_dict)['disk_i'],
                                                 'disk_o': disk_io(cont_data_dict)['disk_o']},
                                        'network': {'rx': network_throughput(cont_data_dict)['rx'],
                                                    'tx': network_throughput(cont_data_dict)['tx']}}

                print("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
                print("Name : {} | Short ID : {} ".format(cont.name, cont.short_id))
                print("CPU : {}%".format(cpu_usage(cont_data_dict)))
                print("Memory/Limit : {}/{} Bytes | Memory % : {}%".format(memory_usage(cont_data_dict)['memory'],
                                                                           memory_usage(cont_data_dict)['memory_limit'],
                                                                           memory_usage(cont_data_dict)['memory_percent']))
                print("Disk I/O : {}/{} Bytes".format(disk_io(cont_data_dict)['disk_i'],
                                                      disk_io(cont_data_dict)['disk_o']))
                print("Network rx/tx : {}/{} Bytes".format(network_throughput(cont_data_dict)['rx'],
                                                           network_throughput(cont_data_dict)['tx']))
        else:
            for cont in containers:
                cont_data_dict = cont.stats(decode=False, stream=False)

                data_dict[cont.name] = {'short_id': cont.short_id,
                                        'cpu': {'cpu_usage': cpu_usage(cont_data_dict)},
                                        'memory': {'memory': memory_usage(cont_data_dict)['memory'],
                                                   'memory_limit': memory_usage(cont_data_dict)['memory_limit'],
                                                   'memory_percent': memory_usage(cont_data_dict)['memory_percent']},
                                        'disk': {'disk_i': disk_io(cont_data_dict)['disk_i'],
                                                 'disk_o': disk_io(cont_data_dict)['disk_o']},
                                        'network': {'rx': network_throughput(cont_data_dict)['rx'],
                                                    'tx': network_throughput(cont_data_dict)['tx']}}

        # data_json = json.dumps(data_dict)
        post = data_dict
        db.containers_data.insert_one(post).inserted_id
        print("\n_ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
        print("JSON text here : ")
        print(data_json)
        time.sleep(10)


def main():
    print("*** MONITORING ***")
    print("Do you want to see stream of the monitoring ?")
    answer = False
    while answer is False:
        x = input("y/n : ")
        if x == "y":
            answer = True
            os.system("clear")
            run_monitoring(True)
        elif x == "n":
            answer = True
            os.system("clear")
            run_monitoring(False)
        else:
            print("Please enter y for yes or n for no.")
            time.sleep(1)


if __name__ == '__main__':
    main()
