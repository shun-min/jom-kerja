# import google
import requests

import json
from datetime import datetime, timedelta
from pathlib import Path

from google.transit import gtfs_realtime_pb2

from constants import *
from models import *


class DataCtrl(object):
    config: Configs = None
    traffic: Union[BusInfo, TrainInfo] = None
    weather: WeatherInfo = None
    active_trip: Trip = None

    def get_config(self):
        with open(Path("./src/tool.json"), "r") as x:
            data = json.load(x)
            gen = data["general"]
            trips = list()
            for t in data['trips']:
                trips.append(Trip(**t))

            self.config = Configs(
                general=GeneralSettings(**gen),
                trips=trips,
            )

    def filter_req_routes(
        self,
        full_feed  # response entity from GTFS-R API
    ) -> None:
        routes = self.active_trip.routes
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
            
            t_start = trip.duration_start
            t_end = trip.duration_end
            start_time = datetime.strptime(
                rf"{now.year}-{now.month}-{now.day} {t_start["h"]}:{t_start["m"]}", "%Y-%m-%d %H:%M"
            ).astimezone()
            end_time = datetime.strptime(
                rf"{now.year}-{now.month}-{now.day} {t_end["h"]}:{t_end["m"]}", "%Y-%m-%d %H:%M"
            ).astimezone()
            if now >= start_time and now <= end_time:
                self.active_trip = trip

    def process_traffic(
        self,
    ) -> None:
        routes = list()
        for r in self.active_trip.routes:
            if r["vehicle"] == VEHICLE_BUS:        
                response = requests.get(BUS_KL_URL)
                feed = gtfs_realtime_pb2.FeedMessage()
                try:
                    feed.ParseFromString(response.content)
                # except google.protobuf.message.DecodeError:
                except Exception as e:
                    pass
                    
                filtered_routes = self.filter_req_routes(
                    full_feed=feed,
                )
                if not filtered_routes:
                    routes.append(
                        BusInfo(
                            bus_id="Not active",
                            plate_num="null"
                        )
                    )
                for ent in filtered_routes:
                    routes.append(
                        BusInfo(
                            bus_id=ent.vehicle.trip.route_id,
                            plate_num=ent.vehicle.vehicle.license_plate
                        )
                    )
            elif r["vehicle"] == VEHICLE_TRAIN:
                response = requests.get(LRT_STAT_URL)
                if not response.ok:
                    return
                res = response.json()
                for rail_line in res["Data"]:
                    if rail_line["LineID"] not in r["code"]:
                        continue
                    routes.append(
                        TrainInfo(
                            line_id=rail_line["LineID"],
                            status=rail_line["Status"],
                        )
                    )
                    break
            else:
                return
        
        self.traffic = routes

    def fetch_weather(self) -> None:
        FULL_ENDPOINT = rf"{WEATHER_URL}{self.active_trip.location}"
        response = requests.get(FULL_ENDPOINT)
        if not response.ok:
            return "Cannot get weather data. "
        data = response.json()
        self.weather = WeatherInfo(
            morning=data[-1]['morning_forecast'],
            afternoon=data[-1]['afternoon_forecast'],
            night=data[-1]['night_forecast'],
            min_temp=data[-1]['min_temp'],
            max_temp=data[-1]['max_temp'],
        )


class PergiKerja():
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl: DataCtrl = ctrl
        self.config = ctrl.config

    def construct_msg(self) -> str:
        msg = f"Weather\n\nStatus: {self.ctrl.weather.morning}\nMax temp: {self.ctrl.weather.max_temp}\n\nTraffic"
        for trf in self.ctrl.traffic:
            trf: Union[BusInfo, TrainInfo]
            if isinstance(trf, BusInfo):
                msg += f"\nBus ID: {trf.bus_id}\nPlate: {trf.plate_num}\n"
            elif isinstance(trf, TrainInfo):
                msg += f"\nTrain Line: {trf.line_id}\nStatus: {trf.status}"
        return msg

    def main(self) -> None:       
        self.ctrl.process_traffic()
        self.ctrl.fetch_weather()
        # TODO: Add process_weather
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
        
    ctrl = DataCtrl()
    ctrl.get_config()
    ctrl.fetch_trips()
    
    interval = int(ctrl.config.general.interval)  # minutes
    delta = timedelta(minutes=interval)
    start_time = datetime.now()
    running = True
    while running:
        time_diff = datetime.now() - start_time
        if (time_diff.seconds > 0 or time_diff.microseconds > 20) and time_diff.seconds < delta.seconds:
            continue

        if not ctrl.active_trip:
            print("No active trip")
        else:
            proc = PergiKerja(
                ctrl=ctrl
            )
            proc.main()
