import uuid
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from src.core.primitives.visualization_sink import VisualizationSink
from src.core.primitives.financial_insight import FinancialInsight, InsightNode, InsightEdge, QuantSummary
from src.core.services.visualization_sink.graph_utils import attach_lazy_readers, derive_visualizer_prompt

from src.core.services.visualization_sink_factory import VisualizationSinkFactory, VisualizationSinkFactoryError
from src.interfaces.protocols import QuantLLMProtocol

logger = logging.getLogger(__name__)

# TODO (Jac): BEGIN - Replace this Python block with Jac walker + by llm() equivalent
class StubQuantLLMProvider:
    """
    MVP Stub implementation of QuantLLMProtocol.
    In Phase 2, this provides basic schema/data for testing the factory.
    By default, it raises NotImplementedError to trigger the synthetic fallback
    and preserve backwards compatibility for existing tests.
    """
    def generate_schema(self, prompt: str) -> Dict[str, Any]:
        raise NotImplementedError("Actual LLM schema generation not yet implemented.")

    def generate_insight_data(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Actual LLM insight data generation not yet implemented.")
# TODO (Jac): END - Jac replacement block

def _load_synth_if_exists(file_path: Path, prompt: str, default_id: str, default_at: str) -> VisualizationSink:
    if file_path.exists():
        with open(file_path, "r") as f:
            data = json.load(f)
        # We preserve the original data as much as possible for testing
        return VisualizationSink.from_dict(data)
    
    # Fallback to a minimal sink if file is missing (shouldn't happen in test env)
    return VisualizationSink(
        insight_id=default_id,
        prompt=prompt,
        created_at=default_at,
        quant_summary=QuantSummary("Stub", "File not found")
    )

def _create_synthetic_fallback(prompt: str) -> VisualizationSink:
    insight_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    # Realistic stub generation based on prompt text
    prompt_upper = prompt.upper()
    
    # Check for specific prompts from synthdata 6-9
    # Paths are relative to project root
    synth_dir = Path("data/raw/synthetic_visualization_sinks")
    
    if "RISK ASSESSMENT" in prompt_upper and "META" in prompt_upper:
        return _load_synth_if_exists(synth_dir / "synthdata6.json", prompt, insight_id, created_at)
    elif "DEEP DIVE" in prompt_upper and "META" in prompt_upper:
        return _load_synth_if_exists(synth_dir / "synthdata7.json", prompt, insight_id, created_at)
    elif "REBALANCING" in prompt_upper and ("META" in prompt_upper or "PLTR" in prompt_upper):
        return _load_synth_if_exists(synth_dir / "synthdata8.json", prompt, insight_id, created_at)
    elif "COMPARE" in prompt_upper and "META" in prompt_upper and "PLTR" in prompt_upper:
        return _load_synth_if_exists(synth_dir / "synthdata9.json", prompt, insight_id, created_at)
    
    nodes = []
    edges = []
    root_node_id = "root"
    
    if "META" in prompt_upper:
        nodes.append(InsightNode(
            node_id="root",
            schema={"type": "ticker_info"},
            data={"symbol": "META", "price": 490.23, "change": "+1.2%"}
        ))
        quant_summary = QuantSummary(
            title="META Analysis",
            summary_text="Meta shows strong correlation with social media trends.",
            key_metrics={"P/E": 25.4, "Volume": "12M"}
        )
        visualizer_pseudo_prompt = "Draw a bull-eye chart centered on META's current valuation."
        suggested_chart_types = ["annotated_line"]
    elif "S&P" in prompt_upper or "SPY" in prompt_upper:
        nodes.append(InsightNode(
            node_id="root",
            schema={"type": "index_info"},
            data={"name": "S&P 500", "value": 5200.45, "trend": "Bullish"}
        ))
        quant_summary = QuantSummary(
            title="S&P 500 Market Insight",
            summary_text="Overall market sentiment is positive following recent earnings.",
            key_metrics={"RSI": 62, "MACD": "Strong Buy"}
        )
        visualizer_pseudo_prompt = "Render a heatmap of S&P 500 sectors."
        suggested_chart_types = ["heatmap"]
    else:
        nodes.append(InsightNode(
            node_id="root",
            schema={"type": "generic_insight"},
            data={"topic": "General Market", "status": "Stable"}
        ))
        quant_summary = QuantSummary(
            title="General Market Overview",
            summary_text="Generic market data analysis.",
            key_metrics={"Volatility": "Low"}
        )
        visualizer_pseudo_prompt = "Show a network graph of related financial entities."
        suggested_chart_types = ["network_graph"]

    return VisualizationSink(
        insight_id=insight_id,
        prompt=prompt,
        created_at=created_at,
        quant_summary=quant_summary,
        nodes=tuple(nodes),
        edges=tuple(edges),
        root_node_id=root_node_id,
        visualizer_pseudo_prompt=visualizer_pseudo_prompt,
        suggested_chart_types=suggested_chart_types
    )

def create_visualization_sink(prompt: str, financial_insight: Optional[FinancialInsight] = None) -> VisualizationSink:
    """
    Public API to create a VisualizationSink.
    If financial_insight is provided, it derives the sink from it.
    Otherwise, it falls back to the existing synthetic/factory path.
    """
    if financial_insight:
        logger.info(f"Creating visualization sink from provided FinancialInsight (ID: {financial_insight.insight_id})")

        # Derive sink from financial_insight
        enriched_nodes = attach_lazy_readers(financial_insight.nodes)
        
        # Use provided visualizer prompt/chart types if available, otherwise derive
        visualizer_prompt = financial_insight.visualizer_pseudo_prompt or derive_visualizer_prompt(financial_insight)
        suggested_chart_types = financial_insight.suggested_chart_types or ["annotated_line", "heatmap"]

        return VisualizationSink(
            insight_id=financial_insight.insight_id,
            prompt=financial_insight.prompt,
            created_at=datetime.now(timezone.utc).isoformat(),
            quant_summary=financial_insight.quant_summary,
            nodes=enriched_nodes,
            edges=financial_insight.edges,
            root_node_id=financial_insight.root_node_id,
            visualizer_pseudo_prompt=visualizer_prompt,
            suggested_chart_types=suggested_chart_types
        )

    # Legacy path (Phase 2): Attempts to use the VisualizationSinkFactory first, falls back to synthetic data.
    # TODO (Jac): BEGIN - Replace this block with direct Jac walker call
    # walker build_visualization_sink { ... }
    try:
        # In a real scenario, the llm_provider would be injected or retrieved from session state.
        # For now we use the stub for testing the factory flow.
        llm_provider = StubQuantLLMProvider()
        return VisualizationSinkFactory.create(prompt, llm_provider)
    except Exception as e:
        logger.info(f"VisualizationSinkFactory failed (expected for stubs), falling back to synthetic: {e}")
        return _create_synthetic_fallback(prompt)
    # TODO (Jac): END - Jac replacement block
