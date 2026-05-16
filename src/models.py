from dataclasses import asdict, dataclass
from typing import Annotated, Any, List, Dict, TypeVar, Union, Optional

# TODO: use pydantic


@dataclass
class Configs:
    general: GeneralSettings
    trips: List[Trip]


@dataclass
class GeneralSettings:
    timezone: str
    interval: str


@dataclass
class Trip:
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
    bus_id: Optional[str] = "-"
    plate_num: Optional[str] = "-"
    line_id: Optional[str] = ""
    status: Optional[str] = "inactive"


@dataclass
class WeatherInfo():
    morning: str = "No morning weather"
    afternoon: str = "No afternoon weather"
    night: str = "No night weather"
    max_temp: str = "-"
    min_temp: str = "-"
