import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from google.transit import gtfs_realtime_pb2
from models import *


class DataCtrl(object):
    traffic: BusRoute = None
    weather: WeatherInfo = None
    config: Configs = None

    def get_config(self):
        with open(Path("./src/tool.json"), "r") as x:
            self.config = Configs(
                # json.load(x) # convert to attribes
            )

    def filter_req_routes(
        self,
        full_feed
    ) -> None:
        your_routes = self.config.bus_routes
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
        self.ctrl.get_config()

    def construct_msg(self) -> str:
        msg = f"Weather: {self.ctrl.weather.desc_morning}\n{self.ctrl.weather.max_temp}\n"
        if self.ctrl.traffic:
            msg += f"\nBus Route: {self.ctrl.traffic.id} {self.ctrl.traffic.plate_num}"
        return msg

    def main(self) -> None:
        interval = self.ctrl.config.interval  # minutes
        delta = timedelta(minutes=interval)
        running = True
        start_time = datetime.now()
        while running:
            if start_time.hour <= 7 or start_time.hour >= 23:
                running = False
                continue
            time_diff = datetime.now() - start_time
            if time_diff.seconds > 2 and time_diff.seconds < delta.seconds:
                continue
            self.ctrl.fetch_weather()
            self.ctrl.fetch_traffic()
            msg = self.construct_msg()
            print(msg)
            res = requests.post(
                url=r"https://ntfy.sh/jxKz3s8A",
                data=msg,
                headers={
                    "Title": "RapidKL stat and weather"
                }
            )

if __name__ == "__main__":
    proc = PergiKerja()
    proc.main()
