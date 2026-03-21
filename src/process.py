import requests
from datetime import datetime, timedelta
from typing import Dict

from google.transit import gtfs_realtime_pb2
# from pywhatkit.whats import sendwhatmsg
# import pywhatkit
from models import BusRoute, WeatherInfo


class DataCtrl(object):
    traffic: BusRoute = None
    weather: WeatherInfo = None

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
        routes = list()
        for ent in filtered_routes:
            routes = BusRoute(
                id=ent.vehicle.trip.route_id,
                plate_num=ent.vehicle.vehicle.license_plate
            )
        self.traffic = routes

    def fetch_weather(self) -> None:
        url = r"https://api.data.gov.my/weather/forecast/?contains=Subang@location__location_name"
        response = requests.get(url)
        if not response.ok:
            return "Cannot get weather data. "
        data = response.json()
        self.weather = WeatherInfo(
            desc_morning=data[-1]['morning_forecast'],
            min_temp=data[-1]['min_temp'],
            max_temp=data[-1]['max_temp'],
        )


class PergiKerja():
    def __init__(self):
        super().__init__()
        self.ctrl = DataCtrl()
        # self.setup_ui()

    def construct_msg(self) -> str:
        msg = (
            f"{self.ctrl.weather.desc_morning}\n{self.ctrl.weather.max_temp}\n",
        )
        if self.ctrl.traffic:
            msg += f"\n{self.ctrl.traffic.id} {self.ctrl.traffic.plate_num}"
        return msg

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
            msg = self.construct_msg()
            print(msg)
            # sendwhatmsg(
            #     phone_no="+60122037682",
            #     message=msg,
            #     time_hour=start_time.hour,
            #     time_min=start_time.minute + 5,
            #     wait_time=2,
            # )

if __name__ == "__main__":
    # app = QApplication([])
    proc = PergiKerja()
    # window.setWindowTitle("Reminder")
    # window.setWindowFlags(window.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint)
    # window.setWindowFlags(window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
    # window.showMaximized()
    # window.resize(800, 600)
    # window.main()
    # app.exec()
    proc.main()
