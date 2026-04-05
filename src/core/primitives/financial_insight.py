from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass(frozen=True)
class InsightNode:
    node_id: str
    schema: Dict[str, Any]
    data: Any  # data can be Dict or List based on synth data

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InsightNode":
        return cls(**data)

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
