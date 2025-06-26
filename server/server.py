# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

# This will be injected by the starter script
ui_instance = None

class SimplePostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            #print("Received POST data:", data)

            # Call UI update if available
            if ui_instance:
                ui_instance.update_signal.emit(data)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")

    def log_message(self, format, *args):
        return

def start_http_server(port=5000):
    server = HTTPServer(("", port), SimplePostHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"HTTP server running on port {port}")
