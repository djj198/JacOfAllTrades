from dataclasses import dataclass, field, asdict
from typing import Protocol, Any, Dict, List, Optional

@dataclass(frozen=True)
class PromptInput:
    prompt: str
    session_id: str
    mcp_config: Any = field(default_factory=list)
    cwd: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class PromptOutput:
    text: str
    visualization_sink: Optional[Dict[str, Any]] = None
    stop_reason: str = "end_turn"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PromptHandler(Protocol):
    def handle_prompt(self, input_data: PromptInput) -> PromptOutput:
        ...

class QuantLLMProtocol(Protocol):
    """
    Protocol for LLM reasoning related to quantitative insights.
    """
    def generate_schema(self, prompt: str) -> Dict[str, Any]:
        """
        Generates a JSON Schema based on the prompt's data requirements.
        """
        ...

    def generate_insight_data(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates data matching the schema.
        """
        ...
