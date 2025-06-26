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
            response = requests.post('http://192.168.68.150:5000', json=data, timeout=1)
            print(response.text)
        except requests.exceptions.Timeout:
            print("Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            
        i = i + 1
        
        time.sleep(1)
