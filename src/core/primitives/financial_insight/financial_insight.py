from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Union
from src.core.primitives.ticker import Ticker
from src.core.primitives.portfolio.portfolio import Portfolio
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
    def from_dict(cls, data: Dict[str, Any]) -> "QuantSummary":
        if isinstance(data, str):
            return cls(title="Quant Summary", summary_text=data)
        
        # Extract only known fields to be robust to extra fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

@dataclass(frozen=True)
class FinancialInsight:
    insight_id: str
    prompt: str
    quant_summary: QuantSummary
    nodes: tuple[InsightNode, ...] = field(default_factory=tuple)
    edges: tuple[InsightEdge, ...] = field(default_factory=tuple)
    root_node_id: Optional[str] = None
    visualizer_pseudo_prompt: Optional[str] = None
    suggested_chart_types: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['quant_summary'] = self.quant_summary.to_dict()
        d['nodes'] = [node.to_dict() for node in self.nodes]
        d['edges'] = [edge.to_dict() for edge in self.edges]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialInsight":
        data = data.copy()
        quant_summary = QuantSummary.from_dict(data.pop("quant_summary", ""))
        nodes = tuple(InsightNode.from_dict(n) for n in data.pop("nodes", []))
        edges = tuple(InsightEdge.from_dict(e) for e in data.pop("edges", []))

        # Extract only known fields to be robust to extra fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        
        return cls(
            quant_summary=quant_summary,
            nodes=nodes,
            edges=edges,
            **filtered_data
        )
