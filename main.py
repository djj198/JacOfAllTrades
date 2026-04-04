import sys
import asyncio
import logging
from src.io import run_stdio_transport

# Standard logging configuration (output to stderr to avoid corrupting stdio transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

def main() -> None:
    """Thin entry point for the Jac ACP Trading Agent MVP."""
    logger = logging.getLogger("main")
    logger.info("Starting Jac ACP Trading Agent MVP...")
    
    try:
        asyncio.run(run_stdio_transport())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Agent crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
