from dataclasses import dataclass
from typing import Any


@dataclass
class Observation:
    kind: str
    payload: Any
