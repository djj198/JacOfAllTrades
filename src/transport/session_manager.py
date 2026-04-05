from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Session:
    session_id: str
    mcp_config: Any = field(default_factory=list) # Defensive: can be list or dict
    cwd: Optional[str] = None

class SessionManager:
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def create_session(self, session_id: str, mcp_config: Any, cwd: Optional[str] = None) -> Session:
        session = Session(session_id=session_id, mcp_config=mcp_config, cwd=cwd)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def remove_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]
