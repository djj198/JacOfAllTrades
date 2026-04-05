import os
import sys
import asyncio
import logging
from src.transport.stdio_handler import run_stdio_transport

# Ensure the log directory exists
DEFAULT_LOG_PATH = "/home/theodoric/DataspellProjects/JacOfAllTrades/logs/agent.log"
LOG_PATH = os.environ.get("AGENT_LOG_PATH", DEFAULT_LOG_PATH)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Configure logging to file and stderr (stdout is reserved for ACP)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(LOG_PATH)
    ]
)
logging.captureWarnings(True)

logger = logging.getLogger("main")

def main() -> None:
    """Launch the JOAT ACP Agent."""
    logger.info("Starting JOAT ACP Agent...")
    try:
        asyncio.run(run_stdio_transport())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.exception(f"Agent crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
