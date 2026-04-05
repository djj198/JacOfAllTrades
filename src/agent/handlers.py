import logging
from src.interfaces.protocols import PromptInput, PromptOutput
from src.core.services.visualization_sink import create_visualization_sink
from src.core.services.financial_insight import create_financial_insight
from src.core.services.portfolio import get_portfolio_context
from src.core.primitives.financial_insight import FinancialInsight
from src.core.primitives.visualization_sink import VisualizationSink

logger = logging.getLogger(__name__)

class JacPromptHandler:
    """
    High-level synchronous handler for ACP prompts.
    This serves as the future bridge to the Jac graph brain.
    Current implementation is a pure sync core service delegation.
    """
    def handle_prompt(self, input_data: PromptInput) -> PromptOutput:
        logger.info(f"Vibe Pipeline start → prompt: {input_data.prompt} (session={input_data.session_id})")

        # TODO (Jac): BEGIN - This 3-step pipeline will be replaced by a single Jac walker call
        # 1. Portfolio Context (discrete component #1)
        portfolio_ctx = get_portfolio_context(input_data.session_id)   # thin immutable snapshot

        # 2. Insight Engine (discrete component #2)
        financial_insight: FinancialInsight = create_financial_insight(
            prompt=input_data.prompt,
            portfolio_context=portfolio_ctx
        )

        # 3. Visualization Sink creation (discrete component #3)
        visualization_sink: VisualizationSink = create_visualization_sink(
            prompt=input_data.prompt,
            financial_insight=financial_insight   # new optional param
        )
        # TODO (Jac): END

        logger.info(f"Vibe Pipeline complete → insight_id={financial_insight.insight_id}, "
                    f"sink nodes={len(visualization_sink.nodes)}")

        return PromptOutput(
            text=f"Jac Agent analyzed: {input_data.prompt}",
            visualization_sink=visualization_sink.to_dict(),
            stop_reason="end_turn"
        )
