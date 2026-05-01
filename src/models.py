from dataclasses import asdict, dataclass
from typing import Annotated, Any, List, Dict, TypeVar, Union, Optional

# TODO: use pydantic

@dataclass
class Configs():
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(v, (list, tuple)):
                setattr(self, k, [Configs(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, Configs(v) if isinstance(v, dict) else v)
    # time_zone: str
    # work: Dict
    # rest: Dict


@dataclass
class BusRoute():
    id: str
    plate_num: str


@dataclass
class WeatherInfo():
    desc_morning: str
    max_temp: str
    min_temp: str
