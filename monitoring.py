import os
import time

import docker

from Monitoring.data_collect import cpu_usage, memory_usage, memory_limit, disk_io, network
from Monitoring.display import header

client = docker.from_env()


def main():
    while True:
        os.system("clear")
        containers = client.containers.list()
        header()
        print("Number of containers : {}".format(len(containers)))
        if len(containers) > 0:
            for cont in containers:
                stat = cont.stats(decode=False, stream=False)
                print("Name: {} CPU : {:5.2f}%  Mem : {:5.2f}%  Max : {} Bytes  Disk I/O : {}/{} Net rx/tx : {}/{}".format(cont.name, cpu_usage(stat),
                                                                                       memory_usage(stat),
                                                                                       memory_limit(stat),
                                                                                       disk_io(stat)[0],
                                                                                       disk_io(stat)[1],
                                                                                       network(stat)[0],
                                                                                       network(stat)[1]))
        time.sleep(3)


if __name__ == '__main__':
    main()
