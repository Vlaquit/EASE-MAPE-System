def cpu_percentage_calculator(previous_cpu: float, previous_system: float, current_cpu: float, current_system: float,
                              percpu_len: int) -> float:
    if (previous_cpu or previous_system or current_cpu or current_system or percpu_len) is None:
        return None

    cpu_percentage = 0.0

    cpu_delta = current_cpu - previous_cpu
    system_delta = current_system - previous_system

    if system_delta > 0.0 and cpu_delta > 0.0:
        cpu_percentage = (cpu_delta / system_delta) * percpu_len * 100

    return cpu_percentage
