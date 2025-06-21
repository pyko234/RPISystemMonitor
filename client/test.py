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


def get_data():
    return {
            'cpuUsage': random.randint(40, 90),
            'cpuTemp': random.randint(40, 90),
            'gpuUsage': random.randint(1, 99),
            'gpuTemp': random.randint(40, 90),
            'game': "Chillin'",
            'time': time.strftime("%I:%M %p", time.localtime()),
            'fps': 0
        }

def get_stats():
    i = 1
    char = 'a'
    url = 'http://localhost:5000/push'
    while True:
        if char == 'a':
            data = get_data()
        else:
            data = get_data()
            data["game"] = "Dredge"
            data["fps"] = 60
        if i % 5 == 0:
            
            char = 'a' if char == 'b' else 'b'
        
        i = i + 1
        
        try:
            response = requests.post(url, json=data, timeout=2)
            if response.status_code == 200:
                print("Data sent successfully")
            else:
                print("Server responded with status:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("POST failed:", e)
        time.sleep(1)

get_stats()