from Monitoring.calculations import cpu_percentage_calculator


def cpu_usage(stat):
    current_cpu = stat['cpu_stats']['cpu_usage']['total_usage']
    if 'system_cpu_usage' in stat['cpu_stats']:
        current_system = stat['cpu_stats']['system_cpu_usage']
    else:
        current_system = None
    previous_cpu = stat['precpu_stats']['cpu_usage']['total_usage']
    if 'system_cpu_usage' in stat['precpu_stats']:
        previous_system = stat['precpu_stats']['system_cpu_usage']
    else:
        previous_system = None
    if 'percpu_usage' in stat['cpu_stats']['cpu_usage']:
        percpu_len = len(stat['cpu_stats']['cpu_usage']['percpu_usage'])
    else:
        percpu_len = None
    return cpu_percentage_calculator(previous_cpu, previous_system, current_cpu, current_system, percpu_len)


def memory_usage(stat):
    if 'usage' in stat['memory_stats']:
        mem = stat['memory_stats']['usage']
    else:
        return None
    if 'limit' in stat['memory_stats']:
        mem_limit = stat['memory_stats']['limit']
    else:
        return None
    return mem / mem_limit * 100


def memory_limit(stat):
    if 'limit' in stat['memory_stats']:
        mem_limit = stat['memory_stats']['limit']
    else:
        return None
    return mem_limit


def disk_io(stat):
    i = stat['blkio_stats']['io_service_bytes_recursive'][0]['value']
    o = stat['blkio_stats']['io_service_bytes_recursive'][1]['value']
    return [i, o]


def network(stat):
    rx = stat['networks']['eth0']['rx_bytes']
    tx = stat['networks']['eth0']['tx_bytes']
    return [rx, tx]
