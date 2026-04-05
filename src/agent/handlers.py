import logging
from typing import Any, Dict, Callable, Coroutine
from acp import (
    InitializeRequest, InitializeResponse,
    NewSessionRequest as SessionNewRequest,
    NewSessionResponse as SessionNewResponse,
    PromptRequest as SessionPromptRequest,
    PromptResponse as SessionPromptResponse,
    SessionNotification as SessionUpdate,
    PROTOCOL_VERSION
)
from acp.schema import AgentCapabilities as Capabilities, Implementation as AgentInfo, AgentMessageChunk
from .core import JacTradingAgent

logger = logging.getLogger(__name__)

async def handle_initialize(agent: JacTradingAgent, request: InitializeRequest) -> InitializeResponse:
    """Handle ACP initialization and capabilities reporting."""
    logger.info("Initializing Jac ACP Trading Agent MVP")
    return InitializeResponse(
        protocol_version=PROTOCOL_VERSION,
        agent_capabilities=Capabilities(),
        agent_info=AgentInfo(
            name="JacTradingAgentMVP",
            version="0.1.0"
        )
    )

async def handle_session_new(agent: JacTradingAgent, request: SessionNewRequest) -> SessionNewResponse:
    """Handle new session creation and MCP config injection."""
    session_id = request.session_id
    # Safe parsing of injected MCP configuration from DataSpell
    mcp_config = getattr(request, "mcp_config", {})
    
    agent.update_session_mcp(session_id, "default", mcp_config)
    logger.info(f"Session initialized: {session_id}")
    
    return SessionNewResponse(session_id=session_id)

async def handle_session_prompt(
    agent: JacTradingAgent, 
    request: SessionPromptRequest, 
    send_notification: Callable[[Any], Coroutine[Any, Any, None]]
) -> SessionPromptResponse:
    """Process prompt request with streaming updates."""
    
    # 1. Send update notification for responsive UX
    await send_notification(SessionUpdate(
        session_id=request.session_id,
        update=AgentMessageChunk(
            session_update="agent_message",
            text="Analyzing portfolio graph state..."
        )
    ))
    
    # TODO: Add logic to delegate to Jac walkers and by llm() here
    
    # 2. Return final text via notification
    await send_notification(SessionUpdate(
        session_id=request.session_id,
        update=AgentMessageChunk(
            session_update="agent_message",
            text="Hello from Jac ACP Trading Agent MVP. Graph brain coming soon."
        )
    ))
    
    # 3. Signal end of turn
    return SessionPromptResponse(
        stop_reason="end_turn"
    )
