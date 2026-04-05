from dataclasses import dataclass, asdict
from typing import Dict, Any, List
from src.core.primitives.ticker import Ticker

@dataclass(frozen=True)
class Portfolio:
    id: str
    tickers: List[Ticker]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        data = data.copy()
        data['tickers'] = [Ticker.from_dict(t) for t in data['tickers']]
        return cls(**data)
