from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from src.core.primitives.financial_insight.financial_insight import InsightNode, InsightEdge, QuantSummary

@dataclass(frozen=True)
class VisualizationSink:
    insight_id: str
    prompt: str
    created_at: str
    quant_summary: QuantSummary
    nodes: tuple[InsightNode, ...] = field(default_factory=tuple)
    edges: tuple[InsightEdge, ...] = field(default_factory=tuple)
    root_node_id: Optional[str] = None
    visualizer_pseudo_prompt: str = ""
    suggested_chart_types: List[str] = field(default_factory=list)
    rendered_payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['quant_summary'] = self.quant_summary.to_dict()
        d['nodes'] = [node.to_dict() for node in self.nodes]
        d['edges'] = [edge.to_dict() for edge in self.edges]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualizationSink":
        data = data.copy()
        
        # Handle field names from synthetic data
        insight_id = data.pop("insight_id", data.pop("node_id", "unknown"))
        quant_summary = QuantSummary.from_dict(data.pop("quant_summary", ""))
        nodes = tuple(InsightNode.from_dict(n) for n in data.pop("nodes", []))
        edges = tuple(InsightEdge.from_dict(e) for e in data.pop("edges", []))
        
        return cls(
            insight_id=insight_id,
            quant_summary=quant_summary,
            nodes=nodes, # type: ignore
            edges=edges, # type: ignore
            **data
        )
