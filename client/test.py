import random
import requests
import time
from flask import jsonify

def get_stats():
    return {
            'cpuUsage': random.randint(40, 90),
            'cpuTemp': random.randint(40, 90),
            'gpuUsage': random.randint(1, 99),
            'gpuTemp': random.randint(40, 90),
            'game': "Chillin'",
            'time': time.strftime("%I:%M %p", time.localtime())
        }

while True:
    try:
        requests.post("http://localhost:5000/push", json=get_stats(), timeout=2)
    except Exception as e:
        print("Error pushing data:", e)
    time.sleep(1)