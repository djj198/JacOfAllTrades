import subprocess
import json
import sys
import os
import time
from pprint import pprint
import unittest
from tests.utils import setup_test_logging

class TestStdioIntegration(unittest.TestCase):
    def setUp(self):
        # Ensure we are in the project root
        self.project_root = "/home/theodoric/DataspellProjects/JacOfAllTrades"
        self.main_path = os.path.join(self.project_root, "main.py")
        self.log_path = setup_test_logging(self.id())
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = self.project_root
        # Enable debug logging for transport to see more info in agent.log
        self.env["DEBUG_TRANSPORT"] = "true"
        self.env["AGENT_LOG_PATH"] = self.log_path

    def test_agent_stdio_communication(self):
        """
        Start the agent as a subprocess, send an initialize and prompt request,
        and verify we receive a response containing a visualization sink.
        """
        # Start the agent process
        # Using -u for unbuffered binary stdout/stdin
        process = subprocess.Popen(
            [sys.executable, "-u", self.main_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.env,
            bufsize=1
        )

        try:
            # 1. Send Initialize Request (JSON-RPC 2.0 style as per ACP)
            # ACP usually uses a specific framing or just JSON-RPC over stdio.
            # Based on acp-python-sdk, it's typically JSON-RPC.
            
            init_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocol_version": 1,
                    "agent_info": {"name": "test-client", "version": "1.0.0"}
                }
            }
            process.stdin.write(json.dumps(init_req) + "\n")
            process.stdin.flush()

            # Read Initialize Response
            line = process.stdout.readline()
            if not line:
                stderr = process.stderr.read()
                self.fail(f"No response from agent. Stderr: {stderr}")
            
            init_res = json.loads(line)
            print("\n--- Initialize Response ---")
            pprint(init_res)
            self.assertEqual(init_res.get("id"), 1)

            # 2. Send New Session Request
            session_req = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "session/new",
                "params": {
                    "cwd": self.project_root,
                    "session_id": "test-session-123",
                    "mcpServers": [] # Should be a list as per error
                }
            }
            process.stdin.write(json.dumps(session_req) + "\n")
            process.stdin.flush()

            # Read Session Response
            line = process.stdout.readline()
            session_res = json.loads(line)
            print("\n--- Session Response ---")
            pprint(session_res)
            self.assertEqual(session_res.get("id"), 2)

            # 3. Send Prompt Request (method: session/prompt)
            prompt_req = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "session/prompt",
                "params": {
                    # Prompt must be a list of content blocks
                    "prompt": [
                        {"type": "text", "text": "Analyze META stock performance and correlation with S&P 500"}
                    ],
                    "sessionId": "test-session-123" # ACP uses camelCase for some fields in JSON
                }
            }
            process.stdin.write(json.dumps(prompt_req) + "\n")
            process.stdin.flush()

            # The agent might send notifications (AgentMessageChunk) before the final PromptResponse
            # We need to read until we find the response with id=3
            prompt_res = None
            start_time = time.time()
            while time.time() - start_time < 5: # 5 seconds timeout
                line = process.stdout.readline()
                if not line:
                    break
                res = json.loads(line)
                if res.get("id") == 3:
                    prompt_res = res
                    break
                else:
                    print(f"\n--- Received Notification/Intermediate ---")
                    pprint(res)

            self.assertIsNotNone(prompt_res, "Did not receive PromptResponse within timeout")
            
            print("\n--- Final Prompt Response ---")
            pprint(prompt_res)

            # Verify VisualizationSink presence
            result = prompt_res.get("result", {})
            meta = result.get("_meta", {})
            visualization_sink = meta.get("visualization_sink")

            self.assertIsNotNone(visualization_sink, "VisualizationSink missing in response meta")
            print("\n--- VisualizationSink Contents (pprint) ---")
            pprint(visualization_sink)
            
            self.assertIn("insight_id", visualization_sink)
            self.assertIn("nodes", visualization_sink)
            self.assertIn("edges", visualization_sink)

        finally:
            process.terminate()
            try:
                process.stdin.close()
                process.stdout.close()
                process.stderr.close()
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    unittest.main()
