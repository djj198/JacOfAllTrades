from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class McpConfig:
    """Immutable wrapper for injected MCP configuration."""
    mcp_id: str
    config: Dict[str, Any]

@dataclass(frozen=True)
class SessionState:
    """Per-session state for the ACP agent."""
    session_id: str
    mcp_config: Optional[McpConfig] = None
    # TODO: Add Jac graph reference or session-specific walkers here later
