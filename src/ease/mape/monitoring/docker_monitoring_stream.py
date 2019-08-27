import os
import time

import docker
from old.monitoring_old import get_containers, get_cpu_percent, get_memory, get_disk_io, get_network_throughput


def streaming():
    docker_client = docker.from_env()
    while True:
        containers = get_containers(docker_client)
        os.system("clear")
        print("_________________________")
        print("*** MONITORING STREAM ***")
        print("_________________________")
        print("==> Number of containers : {}".format(len(containers)))
        for cont in containers:
            cont_data_dict = cont.stats(decode=False, stream=False)
            print("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
            print("Name : {} | Short ID : {} ".format(cont.name, cont.short_id))
            print("CPU : {}%".format(get_cpu_percent(cont_data_dict)))
            print("Memory/Limit : {}/{} Bytes | Memory % : {}%".format(get_memory(cont_data_dict)['memory'],
                                                                       get_memory(cont_data_dict)['memory_limit'],
                                                                       get_memory(cont_data_dict)['memory_percent']))
            print("Disk I/O : {}/{} Bytes".format(get_disk_io(cont_data_dict)['disk_i'],
                                                  get_disk_io(cont_data_dict)['disk_o']))

            print("Network rx/tx : {}/{} Bytes".format(get_network_throughput(cont_data_dict)['rx'],
                                                       get_network_throughput(cont_data_dict)['tx']))
        time.sleep(5)


if __name__ == '__main__':
    streaming()
