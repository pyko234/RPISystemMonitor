from SystemStats import get_stats
import requests
import time

def main():
    url = 'http://localhost:5000/push'  # Replace with your Pi’s IP
    while True:
        data = get_stats()

        try:
            response = requests.post(url, json=data, timeout=2)
            if response.status_code == 200:
                print("Data sent successfully")
            else:
                print("Server responded with status:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("POST failed:", e)
        
        time.sleep(1)

if __name__ == "__main__":
    main()