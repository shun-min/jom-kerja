import requests
from datetime import datetime, timedelta

from google.transit import gtfs_realtime_pb2


class PergiKerja(object):
    def fetch_traffic(self):
        feed = gtfs_realtime_pb2.FeedMessage()
        url = r"https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl"
        response = requests.get(url)
        feed.ParseFromString(response.content)
        for ent in feed.entity:
            if "786" not in ent.vehicle.trip.route_id:
                continue
            print(f"Route: {ent.vehicle.trip.route_id}\nPlate: {ent.vehicle.vehicle.license_plate}")

    def fetch_weather(self):
        url = r"https://api.data.gov.my/weather/forecast"
        response = requests.get(url)
        if not response.ok:
            return "Cannot get weather data. "
        data = response.json()
        return data

    def main(self) -> None:
        interval = 20  #TODO: from config
        start_time = datetime.now()
        delta = timedelta(minutes=interval)
        while True:
            if start_time < "7am" or start_time < "10am":
                continue
            time_diff = datetime.now() - start_time
            if time_diff < delta:
                continue
            start_time = datetime.now().strptime()
            self.fetch_traffic()
            self.fetch_weather()

kerja = PergiKerja()
kerja.main()
