from dataclasses import dataclass, field
from typing import Protocol, Any, Dict, List, Optional

@dataclass(frozen=True)
class PromptInput:
    prompt: str
    session_id: str
    mcp_config: Any = field(default_factory=list)
    cwd: Optional[str] = None

@dataclass(frozen=True)
class PromptOutput:
    text: str
    visualization_sink: Optional[Dict[str, Any]] = None
    stop_reason: str = "end_turn"

class PromptHandler(Protocol):
    def handle_prompt(self, input_data: PromptInput) -> PromptOutput:
        ...
