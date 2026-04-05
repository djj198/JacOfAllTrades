import logging
from typing import Any
from src.interfaces.protocols import PromptOutput
from src.core.services.visualization_sink import create_visualization_sink
from src.core.services.financial_insight import create_financial_insight
from src.core.services.portfolio import get_portfolio_context
from src.core.primitives.financial_insight import FinancialInsight
from src.core.primitives.visualization_sink import VisualizationSink

logger = logging.getLogger(__name__)

def vibe_pipeline(
    prompt: str,
    session_id: str,
    mcp_config: Any = None
) -> PromptOutput:
    """Single source of truth for the entire Vibe Pipeline.
    Pure functional orchestration. Returns fully serialized PromptOutput ready for ACP.
    """
    # TODO (Jac): This entire function will become one Jac walker: vibe_pipeline_walker
    
    logger.info(f"Vibe Pipeline start → prompt: {prompt} (session={session_id})")

    # 1. Portfolio Context (discrete component #1)
    # TODO (Jac): This will be a walker call: query_portfolio_context
    portfolio_ctx = get_portfolio_context(session_id)

    # 2. Insight Engine (discrete component #2)
    # TODO (Jac): This will be a walker call: generate_financial_insight
    financial_insight: FinancialInsight = create_financial_insight(
        prompt=prompt,
        portfolio_context=portfolio_ctx
    )

    # 3. Visualization Sink creation (discrete component #3)
    # TODO (Jac): This will be a walker call: generate_visualization_sink
    visualization_sink: VisualizationSink = create_visualization_sink(
        prompt=prompt,
        financial_insight=financial_insight
    )

    logger.info(f"Vibe Pipeline complete → insight_id={getattr(financial_insight, 'insight_id', 'unknown')}, "
                f"sink nodes={len(getattr(visualization_sink, 'nodes', []))}")

    return PromptOutput(
        text=f"Jac Agent analyzed: {prompt}",
        visualization_sink=visualization_sink.to_dict(),
        stop_reason="end_turn"
    )
