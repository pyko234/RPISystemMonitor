import random
import requests
import time
from flask import jsonify

import threading
import subprocess
fps = 0

def get_fps(exe):
    global fps
    proc = subprocess.Popen(
        ["PresentMon-2.3.1-x64.exe", "-no_csv", "-output_stdout", "-process_name", exe],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )

    try:
        for line in proc.stdout:
            try:
                print(line.strip().split(',')[11])
                #fps = 1000.0 / ms_between_presents
            except IndexError:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()


def get_stats():
    return {
            'cpuUsage': random.randint(40, 90),
            'cpuTemp': random.randint(40, 90),
            'gpuUsage': random.randint(1, 99),
            'gpuTemp': random.randint(40, 90),
            'game': "Chillin'",
            'time': time.strftime("%I:%M %p", time.localtime())
        }

threading.Thread(target=get_fps, args=("chrome.exe",)).start()
#while True:
#    print(f"{fps:.1f}")