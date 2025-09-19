import psutil
import time
from pathlib import Path
import subprocess

def read_sensors():
    # Run the C++ binary and capture stdout
    result = subprocess.run(["./SharedMemoryReader.exe"], capture_output=True, text=True)
    
    sensors = {}
    for line in result.stdout.splitlines():
        # Example line: [2] CPU temperature = 31.625 °C
        if "=" in line:
            idx, rest = line.split("]", 1)
            name, value_unit = rest.split("=", 1)
            
            name = name.strip().lstrip()
            value, unit = value_unit.strip().split(" ", 1)
            
            sensors[name] = f"{float(value):.1f} {unit}"
    return sensors

def get_stats():

    sensors = read_sensors()

    mem = psutil.virtual_memory()
    used_gb = (mem.total - mem.available) / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)

    return {
        'cpu_usage': f"{sensors["CPU usage"]}",
        'cpu_temp': f"{sensors["CPU temperature"]}",
        'gpu_usage': f"{sensors["GPU usage"]}",
        'gpu_temp': f"{sensors["GPU temperature"]}",
        'ram_used':  f"{used_gb:.1f}",
        'ram_total': f"{total_gb:.1f}"
    }

if __name__ == "__main__":
    while True:
        print(get_stats())
        time.sleep(5)
