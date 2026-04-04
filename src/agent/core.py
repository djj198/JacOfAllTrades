import logging
from typing import Dict, Any, Optional
from dataclasses import replace
from .models import SessionState, McpConfig

logger = logging.getLogger(__name__)

class JacTradingAgent:
    """Core logic and session management for the Jac ACP Trading Agent MVP."""
    
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}
        # TODO: Initialize global portfolio graph/service here
        
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve existing session state."""
        return self._sessions.get(session_id)
        
    def create_session(self, session_id: str) -> SessionState:
        """Create a new session state."""
        session = SessionState(session_id=session_id)
        self._sessions[session_id] = session
        return session
        
    def update_session_mcp(self, session_id: str, mcp_id: str, config: Dict[str, Any]) -> SessionState:
        """Update session state with injected MCP configuration."""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
            
        new_mcp = McpConfig(mcp_id=mcp_id, config=config)
        updated_session = replace(session, mcp_config=new_mcp)
        self._sessions[session_id] = updated_session
        return updated_session

    # TODO: Implement Jac walker execution and graph traversals
    # TODO: Integrate by llm() logic via Jac graph layer
