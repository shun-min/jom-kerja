from datetime import datetime
from google.transit import gtfs_realtime_pb2
from pathlib import Path
from playsound3 import playsound
from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QSpinBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
import requests


class AlarmUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self) -> None:
        self.main_lyt = QVBoxLayout()

        self.active_chk = QCheckBox()
        self.alarm_lyt = QVBoxLayout()
        self.alarm_lyt.addWidget(self.active_chk)

        self.alarm_h = QSpinBox()
        self.alarm_h.setRange(0, 23)
        self.alarm_h.setMinimumHeight(80)
        self.alarm_m = QSpinBox()
        self.alarm_m.setRange(0, 59)
        self.alarm_m.setMinimumHeight(80)
        self.clock_lyt = QHBoxLayout()
        self.clock_lyt.addWidget(self.alarm_h)
        self.clock_lyt.addWidget(self.alarm_m)
        self.alarm_lyt.addLayout(self.clock_lyt)

        self.main_lyt.addLayout(self.alarm_lyt)

        # weather and traffic
        self.lbl_traffic = QLabel("Traffic")
        self.lbl_weather_ofc = QLabel("Office Weather")
        self.lbl_weather_sktpk = QLabel("Skatepark Weather")
        self.notif_lyt = QVBoxLayout()
        self.notif_lyt.addWidget(self.lbl_traffic)
        self.notif_lyt.addWidget(self.lbl_weather_ofc)
        self.notif_lyt.addWidget(self.lbl_weather_sktpk)

        self.main_lyt.addLayout(self.notif_lyt)

        self.central_wgt = QWidget()
        self.central_wgt.setLayout(self.main_lyt)
        self.setCentralWidget(self.central_wgt)

    def setup_connections(self):
        self.active_chk.checkStateChanged.connect(self.check_alarm)
        self.active_chk.setChecked(False)

    def run(self) -> None:
        while self.active_chk.isChecked():
            time_now = datetime.now()
            # if 
            # self.fetch_traffic()
    
    def check_alarm(self) -> None:
        if self.active_chk.isChecked:
            self.alarm_h.setDisabled(True)
            self.alarm_m.setDisabled(True)
            # self.run()
        else:
            self.alarm_h.setDisabled(False)
            self.alarm_m.setDisabled(False)

    def fetch_traffic(self):
        feed = gtfs_realtime_pb2.FeedMessage()
        url = r"https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl"
        response = requests.get(url)
        feed.ParseFromString(response.content)
        for ent in feed.entity:
            if "786" not in ent.vehicle.trip.route_id:
                continue
            print(f"Route: {ent.vehicle.trip.route_id}\nPlate{ent.vehicle.vehicle.license_plate}")

    def play_audio(self):
        playsound(Path("~/test.mp3"))


if __name__ == "__main__":
    app = QApplication([])
    window = AlarmUI()
    # skyline_ico = QPixmap(r"N:\pipeline\Tools\icons\skyline.ico")
    # window.setWindowIcon(skyline_ico)
    window.setWindowTitle("Reminder")
    window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
    window.setWindowFlags(window.windowFlags() | Qt.WindowMaximizeButtonHint)
    window.showMaximized()
    window.resize(800, 600)
    app.exec()
