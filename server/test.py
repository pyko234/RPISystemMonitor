import time, random
import json, requests

def simulate_updates():
    import random, time
    sample_data = {
        "cpu_usage": random.randint(0, 100),
        "cpu_temp": random.randint(30, 85),
        "gpu_usage": random.randint(0, 100),
        "gpu_temp": random.randint(30, 85),
        "game": "Chillin'",
        "clock": time.strftime("%I:%M %p"),
        "fps": 0
    }
    return sample_data

if __name__ == '__main__':
    char = 'a'
    i = 1
    while True:
        data = simulate_updates()
        if char == 'b':
            data['game'] = "DREDGE"
            data['fps'] = 60
        if i % 5 == 0:
            char = 'a' if char == 'b' else 'b'
        
        try:
            response = requests.post('http://localhost:5000', json=data)
            print(response.status_code)
        except Exception as e:
            print(f"Error connecting: {e}")
        i = i + 1
        
        time.sleep(1)
