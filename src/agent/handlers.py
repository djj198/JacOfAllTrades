import logging
import json
from src.interfaces.protocols import PromptInput, PromptOutput
from src.core.services.visualization_service import create_visualization_sink

logger = logging.getLogger(__name__)

# Hardcoded portfolio path
PORTFOLIO_PATH = "/home/theodoric/DataspellProjects/JacOfAllTrades/data/raw/synthetic_visualization_sinks/portfolio.json"

class JacPromptHandler:
    """
    High-level synchronous handler for ACP prompts.
    Hardcodes loading of portfolio.json for rich visualization sink generation.
    """
    def handle_prompt(self, input_data: PromptInput) -> PromptOutput:
        logger.info(f"Handling prompt: {input_data.prompt} (session={input_data.session_id})")
        
        # Load portfolio data
        portfolio_data = {}
        try:
            with open(PORTFOLIO_PATH, "r") as f:
                portfolio_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load portfolio.json from {PORTFOLIO_PATH}: {e}")

        # 1. Generate the dynamic visualization sink based on the prompt and portfolio
        sink = create_visualization_sink(prompt=input_data.prompt, portfolio_context=portfolio_data)
        
        # 2. Package output according to Protocol
        sink_dict = sink.to_dict()
        summary = sink_dict.get("quant_summary", {})
        title = summary.get("title", "Insight")
        metrics = summary.get("key_metrics", {})
        metrics_str = "\n".join([f"- **{k}**: {v}" for k, v in metrics.items()])

        full_text = (
            f"### {title}\n\n"
            f"{summary.get('summary_text', '')}\n\n"
            f"**Key Portfolio Metrics:**\n"
            f"{metrics_str}\n\n"
            f"**Visualization Sink JSON:**\n"
            f"```json\n"
            f"{json.dumps(sink_dict, indent=2)}\n"
            f"```"
        )

        return PromptOutput(
            text=full_text,
            visualization_sink=sink_dict,
            stop_reason="end_turn"
        )
