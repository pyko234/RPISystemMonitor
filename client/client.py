from SystemStats import get_stats
import requests
import time

def main():
    url = 'http://192.168.68.150:5000/'  # Replace with your Pi’s IP
    while True:
        data = get_stats()
        #print(data)

        try:
            response = requests.post(url, json=data, timeout=2)
            if not response.status_code == 200:
                print("Server responded with status:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("POST failed:", e)
        
        time.sleep(1)

if __name__ == "__main__":
    main()