from typing import List, Any
from src.core.primitives.financial_insight import InsightNode, FinancialInsight

def build_insight_nodes(nodes_data: List[Any]) -> tuple[InsightNode, ...]:
    """Convert raw node data into InsightNode primitives."""
    return tuple(InsightNode.from_dict(n) if isinstance(n, dict) else n for n in nodes_data)

def attach_lazy_readers(nodes: tuple[InsightNode, ...]) -> tuple[InsightNode, ...]:
    """Enrich nodes with any required lazy data readers (DataRefs)."""
    # In Phase 3, this is a pure-functional pass-through or minimal enrichment.
    return nodes

def derive_visualizer_prompt(financial_insight: FinancialInsight) -> str:
    """Derive a visualizer-specific pseudo-prompt from a FinancialInsight."""
    return f"Visualizing {financial_insight.prompt} (ID: {financial_insight.insight_id})"
