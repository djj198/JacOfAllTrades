import os
import logging
from typing import Optional

def setup_test_logging(test_id: str, is_integration: bool = False) -> str:
    """Sets up logging for a specific test case."""
    log_dir = "/home/theodoric/DataspellProjects/JacOfAllTrades/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Sanitize test_id for filename
    sanitized_id = test_id.replace('.', '_')
    log_filename = f"agent-{sanitized_id}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    # Truncate old log if it exists to keep it fresh per test
    with open(log_path, "w") as f:
        f.truncate(0)

    # Configure root logger for the current process (for unit tests or bridge logs in integration tests)
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_path)
        ]
    )
    logging.captureWarnings(True)
    
    return log_path
