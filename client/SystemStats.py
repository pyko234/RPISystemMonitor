import wmi
import os
import re
import psutil
import time
import subprocess
import threading
from pathlib import Path


def get_stats():

    sys_wmi = wmi.WMI()
    ohm_wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")

    for sensor in ohm_wmi.Sensor():
        if sensor.Name == "GPU Core" and sensor.SensorType == "Load":
            gpu_usage = sensor.value
        elif sensor.Name == "GPU Core" and sensor.SensorType == "Temperature":
            gpu_temp = sensor.value
        elif sensor.Name == "CPU Package":
            cpu_temp = sensor.value
        elif sensor.Name == "CPU Total":
            cpu_usage = sensor.value

    mem = psutil.virtual_memory()
    used_gb = (mem.total - mem.available) / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)

    return {
        'cpu_usage': f"{cpu_usage:.1f}",
        'cpu_temp': f"{cpu_temp:.1f}",
        'gpu_usage': f"{gpu_usage:.1f}",
        'gpu_temp': f"{gpu_temp:.1f}",
        'ram_used':  f"{used_gb:.1f}",
        'ram_total': f"{total_gb:.1f}"
    }

if __name__ == "__main__":
    while True:
        print(get_stats())
        time.sleep(5)
