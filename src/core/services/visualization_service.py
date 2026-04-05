import uuid
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any
from src.core.primitives.visualization_sink import VisualizationSink
from src.core.primitives.financial_insight import InsightNode, InsightEdge, QuantSummary

from src.core.services.visualization_sink_factory import VisualizationSinkFactory
from src.core.providers.stub_quant_llm_provider import StubQuantLLMProvider

logger = logging.getLogger(__name__)

def create_visualization_sink(prompt: str, portfolio_context: Dict[str, Any] | None = None) -> VisualizationSink:
    """
    Public API to create a VisualizationSink.
    Phase 2: Uses the StubQuantLLMProvider with portfolio context.
    """
    try:
        # Instantiate the new portfolio-aware provider
        llm_provider = StubQuantLLMProvider(portfolio_context=portfolio_context)
        return VisualizationSinkFactory.create(prompt, llm_provider)
    except Exception as e:
        logger.error(f"VisualizationSinkFactory failed: {e}")
        # Fallback to simple sink if something goes wrong
        return VisualizationSink(
            insight_id=str(uuid.uuid4()),
            prompt=prompt,
            created_at=datetime.now(timezone.utc).isoformat(),
            quant_summary=QuantSummary("Error", f"Failed to generate visualization: {e}")
        )
