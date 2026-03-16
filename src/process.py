import requests
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict

from google.transit import gtfs_realtime_pb2
from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)


class DataCtrl(object):
    traffic: Dict = None
    weather: Dict = None

    def filter_req_routes(
        self,
        full_feed
    ) -> None:
        your_routes = ["786", "787"] # get from configs
        routes = [
            ent for ent in full_feed.entity
            if ent.vehicle.trip.route_id in your_routes
        ]
        return routes

    def fetch_traffic(self):
        feed = gtfs_realtime_pb2.FeedMessage()
        url = r"https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl"
        response = requests.get(url)
        feed.ParseFromString(response.content)
        filtered_routes = self.filter_req_routes(
            full_feed=feed,
        )
        for ent in filtered_routes:
            print(f"Route: {ent.vehicle.trip.route_id}\nPlate: {ent.vehicle.vehicle.license_plate}")

    def fetch_weather(self) -> None:
        url = r"https://api.data.gov.my/weather/forecast/?contains=Subang@location__location_name"
        response = requests.get(url)
        if not response.ok:
            return "Cannot get weather data. "
        data = response.json()
        self.traffic = data


class PergiKerja(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ctrl = DataCtrl()
        self.setup_ui()

    def setup_ui(self):
        self.main_lyt = QVBoxLayout()

        # weather and traffic
        self.lbl_traffic = QLabel("rapidKL status")
        self.lbl_weather_ofc = QLabel("Office Weather")
        self.lbl_weather_sktpk = QLabel("Skatepark Weather")
        self.info_traffic = QLineEdit()
        self.info_weather_office = QLabel("rapidKL status")
        self.info_weather_sp = QLabel("rapidKL status")
        self.notif_lyt = QVBoxLayout()
        self.notif_lyt.addWidget(self.lbl_traffic)
        self.notif_lyt.addWidget(self.lbl_weather_ofc)
        self.notif_lyt.addWidget(self.lbl_weather_sktpk)

        self.main_lyt.addLayout(self.notif_lyt)

        self.central_wgt = QWidget()
        self.central_wgt.setLayout(self.main_lyt)
        self.setCentralWidget(self.central_wgt)

    def update_info(self):
        # self.
        pass

    def main(self) -> None:
        interval = 20  #TODO: from config
        delta = timedelta(minutes=interval)
        running = True
        start_time = datetime.now()
        while running:
            if start_time.hour <= 7 or start_time.hour >= 10:
                running = False
            time_diff = datetime.now() - start_time
            if time_diff.seconds > 2 and time_diff.seconds < delta.seconds:
                continue
            self.ctrl.fetch_weather()
            self.ctrl.fetch_traffic()
            self.update_info()

if __name__ == "__main__":
    app = QApplication([])
    window = PergiKerja()
    # win_ico = QPixmap(r"")
    # window.setWindowIcon(win_ico)
    window.setWindowTitle("Reminder")
    window.setWindowFlags(window.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint)
    window.setWindowFlags(window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
    window.showMaximized()
    window.resize(800, 600)
    window.main()
    app.exec()
