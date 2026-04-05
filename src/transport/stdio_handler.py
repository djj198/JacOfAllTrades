import logging
from acp import run_agent
from src.transport.acp_transport import AcpTransport
from src.transport.acp_bridge import AcpBridge
from src.transport.session_manager import SessionManager
from src.agent.handlers import JacPromptHandler

logger = logging.getLogger(__name__)

async def run_stdio_transport() -> None:
    """Entry point to launch the ACP agent over stdio."""
    # Setup dependencies according to the architecture
    handler = JacPromptHandler()
    bridge = AcpBridge(handler)
    session_manager = SessionManager()
    
    agent = AcpTransport(bridge, session_manager)
    
    logger.info("Launching JOAT ACP Agent over stdio...")
    await run_agent(agent)
