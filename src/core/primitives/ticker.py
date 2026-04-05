from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class Ticker:
    symbol: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticker":
        return cls(**data)
