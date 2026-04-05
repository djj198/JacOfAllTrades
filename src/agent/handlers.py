import logging
from src.interfaces.protocols import PromptInput, PromptOutput
from src.core.services.visualization_service import create_visualization_sink

logger = logging.getLogger(__name__)

class JacPromptHandler:
    """
    High-level synchronous handler for ACP prompts.
    This serves as the future bridge to the Jac graph brain.
    Current implementation is a pure sync core service delegation.
    """
    def handle_prompt(self, input_data: PromptInput) -> PromptOutput:
        logger.info(f"Handling prompt: {input_data.prompt} (session={input_data.session_id})")
        
        # 1. Generate the dynamic visualization sink based on the prompt
        # In the future, this will call Jac walkers.
        sink = create_visualization_sink(input_data.prompt)
        
        # 2. Package output according to Protocol
        return PromptOutput(
            text=f"Jac Agent analyzed: {input_data.prompt}",
            visualization_sink=sink.to_dict(),
            stop_reason="end_turn"
        )
