from dataclasses import asdict, dataclass
from typing import Annotated, Any, List, Dict, TypeVar, Union, Optional

# TODO: use pydantic

@dataclass
class Configs():
    bus_routes: List
    interval: int


@dataclass
class BusRoute():
    id: str
    plate_num: str


@dataclass
class WeatherInfo():
    desc_morning: str
    max_temp: str
    min_temp: str
