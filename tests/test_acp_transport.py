import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.transport.acp_transport import AcpTransport
from src.transport.session_manager import SessionManager
from src.transport.acp_bridge import AcpBridge
from src.interfaces.protocols import PromptInput, PromptOutput

class TestAcpTransport(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = MagicMock(spec=AcpBridge)
        self.bridge.process_prompt = AsyncMock()
        self.session_manager = SessionManager()
        self.transport = AcpTransport(self.bridge, self.session_manager)
        self.transport.client = AsyncMock()

    def test_prompt_flow(self) -> None:
        # 1. Create session
        self.session_manager.create_session("s1", {"token": "abc"}, "/cwd")
        
        # 2. Mock bridge output
        mock_output = PromptOutput(text="Result", visualization_sink={"nodes": []})
        self.bridge.process_prompt.return_value = mock_output
        
        # 3. Call prompt
        loop = asyncio.new_event_loop()
        try:
            response = loop.run_until_complete(self.transport.prompt("Hello", "s1"))
            
            # Assertions
            self.bridge.process_prompt.assert_called_once()
            call_args = self.bridge.process_prompt.call_args[0][0]
            self.assertIsInstance(call_args, PromptInput)
            self.assertEqual(call_args.prompt, "Hello")
            self.assertEqual(call_args.mcp_config, {"token": "abc"})
            
            self.assertEqual(response.field_meta["visualization_sink"], {"nodes": []})
            self.assertEqual(self.transport.client.session_update.call_count, 2)
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()
