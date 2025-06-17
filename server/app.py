from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
latest_data = {}  # Holds latest pushed stats

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

@app.route('/push', methods=['POST'])
def receive_data():
    global latest_data
    latest_data = request.get_json()
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)