import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from google.transit import gtfs_realtime_pb2

from constants import *
from models import *


class DataCtrl(object):
    config: Configs = None
    traffic: RouteInfo = None
    weather: WeatherInfo = None
    active_trip: Trip = None

    def get_config(self):
        with open(Path("./src/tool.json"), "r") as x:
            data = json.load(x)
            trips = list()
            for t in data['trips']:
                trips.append(Trip(**t))
            self.config = Configs(
                general=data["general"],
                trips=trips,
            )

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

    def fetch_trips(self):
        now = datetime.now().astimezone()
        for trip in self.config.trips:
            if WEEKDAY.get(now.weekday()) not in trip.days:
                continue

            start_time = datetime.strptime(rf"{trip.duration_start["h"]}:{trip.duration_start["m"]}", "%H:%M").astimezone()
            end_time = datetime.strptime(rf"{trip.duration_end["h"]}:{trip.duration_end["m"]}", "%H:%M").astimezone()
            if now >= start_time and now <= end_time:
                self.active_trip = trip

    def process_traffic(
        self,
    ):
        if not self.active_trip:
            self.traffic = [RouteInfo()]
            return
        if self.active_trip.vehicle == VEHICLE_BUS:
            URL = BUS_KL_URL
        elif self.active_trip.vehicle == VEHICLE_TRAIN:
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
            if self.active_trip.vehicle == VEHICLE_BUS:
                routes.append(
                    RouteInfo(
                        id=ent.vehicle.trip.route_id,
                        plate_num=ent.vehicle.vehicle.license_plate
                    )
                )
        self.traffic = routes

    def fetch_weather(self) -> None:
        if not self.active_trip:
            self.weather = WeatherInfo()
            return
        FULL_ENDPOINT = rf"{WEATHER_URL}{self.active_trip.location}"
        response = requests.get(FULL_ENDPOINT)
        if not response.ok:
            return "Cannot get weather data. "
        data = response.json()
        self.weather = WeatherInfo(
            desc=data[-1]['morning_forecast'],
            min_temp=data[-1]['min_temp'],
            max_temp=data[-1]['max_temp'],
        )


class PergiKerja():
    def __init__(self):
        super().__init__()
        self.ctrl = DataCtrl()
        self.ctrl.get_config()

    def construct_msg(self) -> str:
        msg = f"Weather: {self.ctrl.weather.desc}\nMax temp: {self.ctrl.weather.max_temp}\nTraffic:"
        for trf in self.ctrl.traffic:
            trf: RouteInfo
            msg += f"\nID: {trf.id} Plate: {trf.plate_num}"
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
        self.ctrl.fetch_trips()
        self.ctrl.process_traffic()
        self.ctrl.fetch_weather()
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
