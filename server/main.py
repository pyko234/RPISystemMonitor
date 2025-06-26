# start.py
import sys
from PyQt5.QtWidgets import QApplication
from ui import DashboardWindow
import server

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Start UI
    window = DashboardWindow()
    window.show()

    # Inject UI instance into server
    server.ui_instance = window.page  # Or `window`, if update_ui is there

    # Start HTTP server
    server.start_http_server(port=5000)

    # Run event loop
    sys.exit(app.exec_())
