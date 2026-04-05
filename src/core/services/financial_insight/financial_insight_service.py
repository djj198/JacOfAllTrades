import logging
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from src.core.primitives.financial_insight import FinancialInsight, QuantSummary, InsightNode, InsightEdge
from src.core.primitives.portfolio import PortfolioContext

logger = logging.getLogger(__name__)

def create_financial_insight(prompt: str, portfolio_context: Optional[PortfolioContext] = None) -> FinancialInsight:
    """
    Public pure function to create a FinancialInsight.
    """
    # TODO (Jac): BEGIN – replace with walker call
    logger.info(f"Creating financial insight for prompt: {prompt}")
    return _create_synthetic_financial_insight(prompt, portfolio_context)
    # TODO (Jac): END

def _load_insight_synth_if_exists(file_path: Path, prompt: str, default_id: str) -> FinancialInsight:
    """Reconstruct FinancialInsight from synthetic data file."""
    if file_path.exists():
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Adapt VisualizationSink synth data to FinancialInsight
        insight_id = data.get("insight_id", data.get("node_id", default_id))
        quant_summary_data = data.get("quant_summary", "Synthetic Insight")
        
        return FinancialInsight(
            insight_id=insight_id,
            prompt=prompt,
            quant_summary=QuantSummary.from_dict(quant_summary_data),
            nodes=tuple(InsightNode.from_dict(n) for n in data.get("nodes", [])),
            edges=tuple(InsightEdge.from_dict(e) for e in data.get("edges", [])),
            root_node_id=data.get("root_node_id"),
            visualizer_pseudo_prompt=data.get("visualizer_pseudo_prompt"),
            suggested_chart_types=data.get("suggested_chart_types")
        )
    
    return FinancialInsight(
        insight_id=default_id,
        prompt=prompt,
        quant_summary=QuantSummary("Stub", "File not found")
    )

def _create_synthetic_financial_insight(prompt: str, portfolio_context: Optional[PortfolioContext] = None) -> FinancialInsight:
    """
    Builds a realistic FinancialInsight using the existing synthdata JSON files.
    """
    insight_id = str(uuid.uuid4())
    prompt_upper = prompt.upper()
    synth_dir = Path("data/raw/synthetic_visualization_sinks")
    
    # Mapping based on synthdata 6-9
    if "RISK ASSESSMENT" in prompt_upper and "META" in prompt_upper:
        return _load_insight_synth_if_exists(synth_dir / "synthdata6.json", prompt, insight_id)
    elif "DEEP DIVE" in prompt_upper and "META" in prompt_upper:
        return _load_insight_synth_if_exists(synth_dir / "synthdata7.json", prompt, insight_id)
    elif "REBALANCING" in prompt_upper or "OPTIMIZATION" in prompt_upper:
        return _load_insight_synth_if_exists(synth_dir / "synthdata8.json", prompt, insight_id)
    elif "COMPARE" in prompt_upper and "META" in prompt_upper and "PLTR" in prompt_upper:
        return _load_insight_synth_if_exists(synth_dir / "synthdata9.json", prompt, insight_id)

    # Generic fallback
    return FinancialInsight(
        insight_id=insight_id,
        prompt=prompt,
        quant_summary=QuantSummary(title="Generic Insight", summary_text=f"Synthetic insight for: {prompt}"),
        nodes=(InsightNode(node_id="root", schema={"type": "generic"}, data={"topic": prompt}),),
        edges=(),
        root_node_id="root"
    )
