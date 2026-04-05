import unittest
import asyncio
from src.transport.acp_bridge import AcpBridge
from src.interfaces.protocols import PromptInput, PromptOutput

class MockHandler:
    def handle_prompt(self, input_data: PromptInput) -> PromptOutput:
        return PromptOutput(text=f"Handled {input_data.prompt}")

class TestAcpBridge(unittest.TestCase):
    def test_bridge_delegation(self) -> None:
        handler = MockHandler()
        bridge = AcpBridge(handler)
        
        input_data = PromptInput(prompt="test", session_id="s1")
        
        # Run the async process_prompt
        loop = asyncio.new_event_loop()
        try:
            output = loop.run_until_complete(bridge.process_prompt(input_data))
            self.assertEqual(output.text, "Handled test")
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()
