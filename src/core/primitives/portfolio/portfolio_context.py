from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

@dataclass(frozen=True)
class Fundamentals:
    pe_ratio: float
    market_cap_billions: float
    dividend_yield: Optional[float] = None
    eps_growth_next_year: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fundamentals":
        # Extract only known fields to be robust to extra fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    avg_cost_basis: float
    unrealized_pnl: float
    weight_pct: float
    fundamentals: Optional[Fundamentals] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        data = data.copy()
        if data.get('fundamentals'):
            data['fundamentals'] = Fundamentals.from_dict(data['fundamentals'])
        
        # Extract only known fields to be robust to extra fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

@dataclass(frozen=True)
class PortfolioContext:
    portfolio_id: str
    total_value: float
    positions: List[Position]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PortfolioContext":
        data = data.copy()
        if 'positions' in data:
            data['positions'] = [Position.from_dict(p) for p in data['positions']]
        
        # Extract only known fields to be robust to extra fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)
