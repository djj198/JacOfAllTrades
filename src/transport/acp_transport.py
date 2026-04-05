import logging
import time
import os
import json
from typing import Any, Dict, Optional
from acp import (
    Agent, Client, InitializeRequest, InitializeResponse,
    NewSessionRequest, NewSessionResponse, PromptRequest, PromptResponse,
    SessionNotification, PROTOCOL_VERSION
)
from acp.schema import AgentCapabilities, Implementation, AgentMessageChunk, TextContentBlock

from src.transport.session_manager import SessionManager
from src.transport.acp_bridge import AcpBridge
from src.interfaces.protocols import PromptInput

logger = logging.getLogger(__name__)
DEBUG_TRANSPORT = os.environ.get("DEBUG_TRANSPORT", "false").lower() == "true"

class AcpTransport(Agent):
    """
    Thin IO/transport layer delegating to core via AcpBridge.
    Only imports from interfaces/ and transport/ (per decoupling rules).
    """
    def __init__(self, bridge: AcpBridge, session_manager: SessionManager):
        self.bridge = bridge
        self.session_manager = session_manager
        self.client: Client | None = None

    def on_connect(self, conn: Client) -> None:
        self.client = conn

    async def initialize(self, protocol_version: int, **kwargs: Any) -> InitializeResponse:
        logger.info(f"ACP Initialize version={protocol_version}")
        return InitializeResponse(
            protocol_version=PROTOCOL_VERSION,
            agent_capabilities=AgentCapabilities(),
            agent_info=Implementation(
                name="JacHacks-JOAT-Agent",
                version="1.0.0"
            )
        )

    async def new_session(self, cwd: str, **kwargs: Any) -> NewSessionResponse:
        session_id = kwargs.get("session_id", "default-session")
        mcp_config = kwargs.get("mcp_config", {})
        
        logger.info(f"New session: {session_id} (cwd={cwd})")
        self.session_manager.create_session(session_id, mcp_config, cwd)
        
        return NewSessionResponse(session_id=session_id)

    async def prompt(self, prompt: Any, session_id: str, **kwargs: Any) -> PromptResponse:
        start_time = time.time()
        session = self.session_manager.get_session(session_id)
        mcp_config = session.mcp_config if session else {}
        
        input_data = PromptInput(
            prompt=str(prompt),
            session_id=session_id,
            mcp_config=mcp_config,
            cwd=session.cwd if session else None
        )
        
        # UX: Send immediate notification
        if self.client:
            await self.client.session_update(
                session_id=session_id,
                update=AgentMessageChunk(
                    session_update="agent_message_chunk",
                    content=TextContentBlock(type="text", text="[IO] Thinking...")
                )
            )
        
        # Delegate to core logic through async bridge
        output = await self.bridge.process_prompt(input_data)
        
        # UX: Final text update before sending the response result
        if self.client:
             await self.client.session_update(
                session_id=session_id,
                update=AgentMessageChunk(
                    session_update="agent_message_chunk",
                    content=TextContentBlock(type="text", text=output.text)
                )
            )
            
        latency_ms = (time.time() - start_time) * 1000
        sink_dict = output.visualization_sink
        sink_size = len(json.dumps(sink_dict)) if sink_dict else 0
        
        logger.info(
            f"[TRANSPORT] Prompt handled for session={session_id}. "
            f"Total latency={latency_ms:.2f}ms, response_sink_size={sink_size} bytes"
        )
            
        return PromptResponse(
            field_meta={"visualization_sink": sink_dict},
            stop_reason=output.stop_reason
        )
