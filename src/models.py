from dataclasses import asdict, dataclass
from typing import Annotated, Any, Dict, TypeVar, Union, Optional

# TODO: use pydantic

@dataclass
class BusRoute():
    id: str
    plate_num: str


@dataclass
class WeatherInfo():
    id: str
    desc: str
