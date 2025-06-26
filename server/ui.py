import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QTimer, pyqtProperty, QPropertyAnimation, QEasingCurve
import math

class CurvedBarDial(QWidget):    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._usage = 0
        self.temp = 0
        self.min_value = 0
        self.max_value = 100

        self._anim = QPropertyAnimation(self, b"usage")
        self._anim.setDuration(700)  # 300ms animation
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

    def getUsage(self):
        return self._usage

    def setUsage(self, value):
        self._usage = value
        self.update()

    usage = pyqtProperty(float, fget=getUsage, fset=setUsage)

    def setValue(self, usage, temp):
        self.temp = temp
        self._anim.stop()
        self._anim.setStartValue(self._usage)
        self._anim.setEndValue(max(self.min_value, min(self.max_value, float(usage))))
        self._anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        margin = 10
        arc_thickness = 20
        label_height = 25
        arc_height = h - label_height - margin

        rect = QRectF(margin, label_height + 20, w - 2 * margin, arc_height * 2)

        # Arc angles
        start_angle = 180 * 16
        span_angle = -int(180 * 16 * (self._usage / 100))

        # Background arc
        pen_bg = QPen(QColor('#333'), arc_thickness)
        pen_bg.setCapStyle(Qt.FlatCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 180 * 16, -180 * 16)

        # Foreground arc
        pen_fg = QPen(QColor('red'), arc_thickness)
        pen_fg.setCapStyle(Qt.FlatCap)
        painter.setPen(pen_fg)
        painter.drawArc(rect, start_angle, span_angle)

        # Draw labels
        painter.setPen(Qt.red)
        font = painter.font()
        font.setPointSize(18)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self.temp}°C")
        painter.drawText(0, 0, w, label_height, Qt.AlignHCenter | Qt.AlignBottom, f"{self._usage}%")

# This acts like a "frame" or parent container for the layout
class PageWidget(QWidget):
    update_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.update_signal.connect(self.update_ui)

    def init_ui(self):
        self.setStyleSheet("background-color: #222; border-radius: 10px;")

        label_style = "background-color: none;border: none; color: red; font-size: 20px; font-weight: bold"
        
        # Vertical layout
        layout = QVBoxLayout(self)
        
        # Row 1
        row1 = QHBoxLayout()
        cpu_label = QLabel("CPU")
        gpu_label = QLabel("GPU")
        cpu_label.setStyleSheet(label_style)
        gpu_label.setStyleSheet(label_style)
        cpu_label.setAlignment(Qt.AlignCenter)
        gpu_label.setAlignment(Qt.AlignCenter)
        row1.addWidget(cpu_label)
        row1.addWidget(gpu_label)
        layout.addLayout(row1, stretch=1)

        # Row 2
        row2 = QHBoxLayout()
        row2.setContentsMargins(0,20,0,20)
        self.cpu_dial = CurvedBarDial()
        self.cpu_dial.setValue(50, 50)
        self.gpu_dial = CurvedBarDial()
        self.gpu_dial.setValue(50, 50)
        row2.addWidget(self.cpu_dial)
        row2.addWidget(self.gpu_dial)
        layout.addLayout(row2, stretch=7)

        # Row 3
        row3_container = QWidget()
        row3_container.setStyleSheet("background-color: #333333; border: none")
        row3 = QHBoxLayout()
        row3.setContentsMargins(5, 0, 5, 0)
        row3_container.setLayout(row3)
        self.game_label = QLabel("Working on: Chillin'")
        self.clock_label = QLabel("00:00 AM")
        self.fps_label = QLabel("")
        self.fps_label.setFixedWidth(150)
        self.game_label.setStyleSheet(label_style)
        self.clock_label.setStyleSheet(label_style)
        self.fps_label.setStyleSheet(label_style)
        row3.addWidget(self.game_label, alignment=Qt.AlignLeft)
        row3.addWidget(self.fps_label, alignment=Qt.AlignRight)
        row3.addWidget(self.clock_label, alignment=Qt.AlignCenter)
        layout.addWidget(row3_container, stretch=2)


    def update_ui(self, data):
        self.cpu_dial.setValue(data['cpu_usage'], data['cpu_temp'])
        self.gpu_dial.setValue(data['gpu_usage'], data['gpu_usage'])
        self.game_label.setText(f"Working on: {data['game']}")
        self.clock_label.setText(data['time'])

        if data['game'] != "Chillin'":
            self.fps_label.setText(f"FPS: {data['fps']}")
        elif data['game'] == "Chillin'":
            self.fps_label.setText("")


class DashboardWindow(QWidget):
    def __init__(self, width=800, height=480):
        super().__init__()
        self.width = width
        self.height = height
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; border: 2px solid gray;")
        self.setCursor(Qt.BlankCursor)

        self.center()

        self.page = PageWidget(self)
        self.page.setFixedSize(self.width - 40, self.height - 40)
        self.page.move(20, 20)

        # This is to test updating the UI
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.simulate_updates)
        #self.timer.start(1000)

    def center(self):
        # Move the window to the center of the screen
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width) // 2
        y = (screen_geometry.height() - self.height) // 2
        self.move(x, y)

    def simulate_updates(self):
        import random, time
        sample_data = {
            "cpu_usage": random.randint(0, 100),
            "cpu_temp": random.randint(30, 85),
            "gpu_usage": random.randint(0, 100),
            "gpu_temp": random.randint(30, 85),
            "game": "DREDGE",
            "clock": time.strftime("%I:%M %p"),
            "fps": random.choice([30, 60, 120])
        }
        self.page.update_ui(sample_data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())
