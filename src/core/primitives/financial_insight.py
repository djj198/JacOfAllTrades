from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Union
from src.core.primitives.ticker import Ticker
from src.core.primitives.portfolio import Portfolio
from src.core.primitives.data_ref import DataRef

@dataclass(frozen=True)
class InsightNode:
    node_id: str
    schema: Dict[str, Any]
    data: Union[Ticker, Portfolio, DataRef, Dict[str, Any], List[Any], Any]  # data can be Dict or List based on synth data

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Handle the Union types if asdict doesn't do it right, but it should for frozen dataclasses
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InsightNode":
        node_id = data.get("node_id", "")
        schema = data.get("schema", {})
        data_val = data.get("data")

        if isinstance(data_val, dict):
            if "symbol" in data_val and "name" in data_val:
                data_val = Ticker.from_dict(data_val)
            elif "tickers" in data_val and "id" in data_val:
                data_val = Portfolio.from_dict(data_val)
            elif "path" in data_val and "reader_name" in data_val:
                data_val = DataRef.from_dict(data_val)

        return cls(node_id=node_id, schema=schema, data=data_val)

@dataclass(frozen=True)
class InsightEdge:
    source_id: str
    target_id: str
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InsightEdge":
        # Handle flexible field names from synthetic data
        source_id = data.get("source_id") or data.get("source") or data.get("source_node_id") or ""
        target_id = data.get("target_id") or data.get("target") or data.get("target_node_id") or ""
        reasoning = data.get("reasoning") or data.get("insight") or data.get("insight_text") or ""
        return cls(source_id=source_id, target_id=target_id, reasoning=reasoning)

@dataclass(frozen=True)
class QuantSummary:
    title: str
    summary_text: str
    key_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "QuantSummary":
        if isinstance(data, str):
            return cls(title="Quant Summary", summary_text=data)
        return cls(**data)
