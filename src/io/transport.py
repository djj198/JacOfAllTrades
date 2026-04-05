import logging
from typing import Any, Callable, Coroutine
from acp import (
    run_agent, Agent, Client, 
    InitializeRequest, InitializeResponse, 
    NewSessionRequest, NewSessionResponse, 
    PromptRequest, PromptResponse, 
    SessionNotification
)
from ..agent import (
    JacTradingAgent,
    handle_initialize,
    handle_session_new,
    handle_session_prompt
)

logger = logging.getLogger(__name__)

class JacAgentWrapper(Agent):
    """Adapter to bridge JacTradingAgent with the current ACP SDK."""
    def __init__(self, jac_agent: JacTradingAgent):
        self.jac_agent = jac_agent
        self.client: Client | None = None

    def on_connect(self, conn: Client) -> None:
        self.client = conn

    async def initialize(self, protocol_version: int, **kwargs: Any) -> InitializeResponse:
        logger.log(f"Intializing jac agent with version: {protocol_version} and kwargs: {kwargs}")
        request = InitializeRequest(protocol_version=protocol_version, **kwargs)
        return await handle_initialize(self.jac_agent, request)

    async def new_session(self, cwd: str, **kwargs: Any) -> NewSessionResponse:
        logger.log(f"New session requested with cwd: {cwd} and kwargs: {kwargs}")
        request = NewSessionRequest(cwd=cwd, **kwargs)
        return await handle_session_new(self.jac_agent, request)

    async def prompt(self, prompt: Any, session_id: str, **kwargs: Any) -> PromptResponse:
        request = PromptRequest(prompt=prompt, session_id=session_id, **kwargs)
        async def send_notification(notification: SessionNotification) -> None:
            if self.client:
                # The SDK expect the update object directly, not the SessionNotification wrapper
                await self.client.session_update(
                    session_id=notification.session_id,
                    update=notification.update
                )
        return await handle_session_prompt(self.jac_agent, request, send_notification)

async def run_stdio_transport() -> None:
    """Run the agent over stdio using the ACP SDK."""
    agent = JacTradingAgent()
    wrapper = JacAgentWrapper(agent)
    
    logger.info("Starting ACP agent over stdio")
    await run_agent(wrapper)
