import os
import sys
import asyncio
import logging
from src.transport.stdio_handler import run_stdio_transport

# Ensure the log directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "agent.log")

# Configure logging to file and stderr (stdout is reserved for ACP)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(LOG_PATH)
    ]
)

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
