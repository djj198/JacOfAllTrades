import sys
import asyncio
import logging
from typing import Any
from agent_client_protocol import AgentSideConnection, stdio_streams
from ..agent import (
    JacTradingAgent,
    handle_initialize,
    handle_session_new,
    handle_session_prompt
)

logger = logging.getLogger(__name__)

async def run_stdio_transport() -> None:
    """Thin IO layer for stdio JSON-RPC via the ACP SDK."""
    agent = JacTradingAgent()
    
    async with stdio_streams() as (read_stream, write_stream):
        # Establish connection using stdio streams
        connection = AgentSideConnection(read_stream, write_stream)
        
        # Delegate protocol handlers immediately to the core agent logic
        connection.on_initialize = lambda req: handle_initialize(agent, req)
        connection.on_session_new = lambda req: handle_session_new(agent, req)
        
        # Wrap prompt to include the notification capability for streaming
        async def prompt_handler_wrapper(request: Any) -> Any:
            return await handle_session_prompt(agent, request, connection.send_notification)
            
        connection.on_session_prompt = prompt_handler_wrapper
        
        logger.info("Jac ACP Trading Agent MVP is listening on stdio...")
        await connection.listen()
