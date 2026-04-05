import logging
from src.interfaces.protocols import PromptInput, PromptOutput
from src.core.services.vibe_pipeline import vibe_pipeline

logger = logging.getLogger(__name__)

class JacPromptHandler:
    """
    High-level synchronous handler for ACP prompts.
    This serves as the future bridge to the Jac graph brain.
    Current implementation is a pure sync core service delegation.
    """
    def handle_prompt(self, input_data: PromptInput) -> PromptOutput:
        # Thin handler that delegates to the new pure-functional vibe_pipeline
        # Safe attribute access for prompt input fields
        return vibe_pipeline(
            prompt=getattr(input_data, "prompt", ""),
            session_id=getattr(input_data, "session_id", "default"),
            mcp_config=getattr(input_data, "mcp_config", None)
        )
