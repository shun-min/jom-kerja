import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from google.transit import gtfs_realtime_pb2

from constants import *
from models import *


class DataCtrl(object):
    traffic: BusRoute = None
    weather: WeatherInfo = None
    config: Configs = None

    def get_config(self):
        with open(Path("./src/tool.json"), "r") as x:
            data = json.load(x)
            self.config = Configs(**data)

    def filter_req_routes(
        self,
        full_feed
    ) -> None:
        routes = self.config.work.departure.routes
        result = [
            ent for ent in full_feed.entity
            if ent.vehicle.trip.route_id in routes
        ]
        return result

    def process_trip(
        self,
        active_trip: Trip,
    ):
        if active_trip.vehicle == VEHICLE_BUS:
            URL = BUS_KL_URL
        elif active_trip.vehicle == VEHICLE_TRAIN:
            URL = LRT_KELANA_URL
        else:
            return
        response = requests.get(URL)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        filtered_routes = self.filter_req_routes(
            full_feed=feed,
        )
        routes = list()
        for ent in filtered_routes:
            if active_trip.vehicle == VEHICLE_BUS:
                routes.append(
                    BusRoute(
                        id=ent.vehicle.trip.route_id,
                        plate_num=ent.vehicle.vehicle.license_plate
                    )
                )
            else:
                routes.append()
        self.traffic = routes

    def fetch_trips(self):
        now = datetime.now().astimezone()
        active_trips = list()
        for trip in self.config.trips:
            if now.day not in trip.days or now.hour not in trip.time["h"] or now.minute not in trip.time["m"]:
                continue
            active_trips.append(trip)
        
        for t in active_trips:
            self.process_trip(active_trip=t)

    def fetch_weather(self) -> None:
        response = requests.get(WEATHER_URL)
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
        msg = f"Weather: {self.ctrl.weather.desc_morning}\nMax temp: {self.ctrl.weather.max_temp}\nTraffic:"
        if self.ctrl.traffic:
            msg += f"\n{self.ctrl.traffic.id} {self.ctrl.traffic.plate_num}"
        return msg

    def main(self) -> None:
        # interval = self.ctrl.config.interval  # minutes
        # delta = timedelta(minutes=interval)
        # running = True
        # start_time = datetime.now()
        # while running:
        #     if start_time.hour <= 7 or start_time.hour >= 23:
        #         running = False
        #         continue
        #     time_diff = datetime.now() - start_time
        #     if time_diff.seconds > 2 and time_diff.seconds < delta.seconds:
        #         continue
        self.ctrl.fetch_weather()
        self.ctrl.fetch_trips()
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
