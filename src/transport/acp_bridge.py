import asyncio
import time
import logging
import os
import json
from typing import Any
from src.interfaces.protocols import PromptInput, PromptOutput, PromptHandler

logger = logging.getLogger(__name__)
DEBUG_TRANSPORT = os.environ.get("DEBUG_TRANSPORT", "false").lower() == "true"

class AcpBridge:
    def __init__(self, handler: PromptHandler):
        self.handler = handler

    async def process_prompt(self, input_data: PromptInput) -> PromptOutput:
        """
        Pure async bridge that delegates to the synchronous core handler 
        using asyncio.to_thread to avoid blocking the event loop.
        """
        start_time = time.time()
        session_id = input_data.session_id
        
        if DEBUG_TRANSPORT:
            logger.info(f"[BRIDGE] Crossing sync boundary for session={session_id}")
        
        try:
            # Measure serialization size before calling
            input_size = len(json.dumps(input_data.prompt))
            
            if DEBUG_TRANSPORT:
                logger.info(f"[BRIDGE] input_size={input_size} bytes")
            
            output = await asyncio.to_thread(self.handler.handle_prompt, input_data)
            
            latency_ms = (time.time() - start_time) * 1000
            output_size = len(json.dumps(output.visualization_sink))
            
            logger.info(
                f"[BRIDGE] Core execution completed. session={session_id}, "
                f"latency={latency_ms:.2f}ms, sink_size={output_size} bytes"
            )
            
            return output
        except Exception as e:
            logger.exception(f"[BRIDGE] Error in core execution for session={session_id}: {e}")
            raise
