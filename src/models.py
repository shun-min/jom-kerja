from dataclasses import asdict, dataclass
from typing import Annotated, Any, List, Dict, TypeVar, Union, Optional

# TODO: use pydantic


@dataclass
class Configs():
    # def __init__(self, d):
    #     for k, v in d.items():
    #         if isinstance(v, (list, tuple)):
    #             setattr(self, k, [Configs(x) if isinstance(x, dict) else x for x in v])
    #         else:
    #             setattr(self, k, Configs(v) if isinstance(v, dict) else v)
    general: Dict[str, Any]
    trips: List[Trip]


@dataclass
class Trip():
    activity: str
    location: str
    journey: str
    days: List[str]
    duration_start: Dict[str, int]
    duration_end: Dict[str, int]
    vehicle: str
    routes: List[str]


@dataclass
class RouteInfo():
    id: str = "-"
    plate_num: str = "-"


@dataclass
class WeatherInfo():
    morning: str = "No morning weather"
    afternoon: str = "No afternoon weather"
    night: str = "No night weather"
    max_temp: str = "-"
    min_temp: str = "-"
