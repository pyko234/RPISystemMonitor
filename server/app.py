from flask import Flask, render_template, jsonify, request
import time
import threading
import subprocess

app = Flask(__name__)
latest_data = {}  # Holds latest pushed stats
last_update_time = time.time()
screen_on=True
TIMEOUT = 5

def set_display(on):
    global screen_on
    if on and not screen_on:
        print("Turning screen ON")
        subprocess.run("DISPLAY=:0 xrandr --output HDMI-1 --auto", shell=True)
        screen_on = True
    elif not on and screen_on:
        print("Turning screen OFF")
        subprocess.run("DISPLAY=:0 xrandr --output HDMI-1 --off", shell=True)
        screen_on = False

def monitor_connection():
    global last_update_time
    while True:
        print(last_update_time)
        now = time.time()
        if now - last_update_time > TIMEOUT:
            set_display(False)
        else:
            set_display(True)
        time.sleep(1)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

@app.route('/push', methods=['POST'])
def receive_data():
    global latest_data, last_update_time
    latest_data = request.get_json()
    last_update_time = time.time()
    return 'OK', 200

if __name__ == '__main__':
    threading.Thread(target=monitor_connection, daemon=True).start()
    app.run(host='0.0.0.0', debug=False)