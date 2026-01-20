from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class Action:
    name: str
    params: Dict[str, Any]
