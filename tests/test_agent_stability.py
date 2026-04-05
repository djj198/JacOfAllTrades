import subprocess
import json
import sys
import os
import time
import unittest
from pprint import pprint
import logging
from tests.utils import setup_test_logging

class TestAgentStability(unittest.TestCase):
    def setUp(self):
        self.project_root = "/home/theodoric/DataspellProjects/JacOfAllTrades"
        self.main_path = os.path.join(self.project_root, "main.py")
        self.log_path = setup_test_logging(self.id())
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = self.project_root
        self.env["DEBUG_TRANSPORT"] = "true"
        self.env["AGENT_LOG_PATH"] = self.log_path
        
        # Prompts to use for testing
        self.test_prompts = [
            "Analyze META stock performance and correlation with S&P 500",
            "Show PLTR vs XLK Sharpe ratio comparison",
            "Decompose MSFT revenue growth",
            "HPQ vs DELL ROE comparison"
        ]

    def _read_logs(self):
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                return f.read()
        return ""

    def test_agent_stdio_communication_stress(self):
        """
        Open-loop stability test:
        - Launch agent as subprocess once.
        - Run 8 full cycles.
        """
        # Truncate logs at start of test to avoid old errors
        if os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                f.write("")

        # Start the agent process
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
            for cycle in range(8):
                print(f"\n--- Starting Cycle {cycle + 1}/8 ---")
                
                # 1. Initialize
                init_req = {
                    "jsonrpc": "2.0",
                    "id": cycle * 100 + 1,
                    "method": "initialize",
                    "params": {
                        "protocol_version": 1,
                        "agent_info": {"name": "stress-test-client", "version": "1.0.0"}
                    }
                }
                process.stdin.write(json.dumps(init_req) + "\n")
                process.stdin.flush()
                
                line = process.stdout.readline()
                self.assertTrue(line, "No response from agent during initialize")
                init_res = json.loads(line)
                self.assertEqual(init_res.get("id"), init_req["id"])

                # 2. session/new
                session_id = f"stress-session-{cycle}"
                session_req = {
                    "jsonrpc": "2.0",
                    "id": cycle * 100 + 2,
                    "method": "session/new",
                    "params": {
                        "cwd": self.project_root,
                        "sessionId": session_id,
                        "mcpServers": [] # Realistic param
                    }
                }
                process.stdin.write(json.dumps(session_req) + "\n")
                process.stdin.flush()
                
                line = process.stdout.readline()
                self.assertTrue(line, "No response from agent during session/new")
                session_res = json.loads(line)
                self.assertEqual(session_res.get("id"), session_req["id"])

                # 3. session/prompt (4 prompts per cycle)
                for p_idx, prompt_text in enumerate(self.test_prompts):
                    p_id = cycle * 100 + 10 + p_idx
                    prompt_req = {
                        "jsonrpc": "2.0",
                        "id": p_id,
                        "method": "session/prompt",
                        "params": {
                            "prompt": [{"type": "text", "text": prompt_text}],
                            "sessionId": session_id
                        }
                    }
                    
                    start_time = time.time()
                    process.stdin.write(json.dumps(prompt_req) + "\n")
                    process.stdin.flush()

                    prompt_res = None
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break
                        res = json.loads(line)
                        if res.get("id") == p_id:
                            prompt_res = res
                            break
                        # Check for errors in notifications
                        if "error" in res:
                            self.fail(f"Error in notification: {res}")

                    latency_ms = (time.time() - start_time) * 1000
                    self.assertIsNotNone(prompt_res, f"No PromptResponse for prompt: {prompt_text}")
                    self.assertLess(latency_ms, 50, f"Latency too high: {latency_ms:.2f}ms")
                    
                    # Verify VisualizationSink
                    result = prompt_res.get("result", {})
                    meta = result.get("_meta", {})
                    sink = meta.get("visualization_sink")
                    
                    self.assertIsNotNone(sink, "VisualizationSink missing")
                    for field in ["insight_id", "nodes", "edges", "visualizer_pseudo_prompt"]:
                        self.assertIn(field, sink, f"Missing field {field} in sink")
                    
                    print(f"Prompt '{prompt_text[:20]}...' handled in {latency_ms:.2f}ms")

                # Check logs for errors after each cycle
                logs = self._read_logs()
                for error_marker in ["Invalid params", "Internal error", "Background task failed"]:
                    if error_marker in logs:
                        # Find the context of the error if possible
                        self.fail(f"Found error '{error_marker}' in logs during cycle {cycle+1}")

            print("\n--- Stability test completed successfully (8 cycles) ---")

        finally:
            process.terminate()
            try:
                # Properly close pipes to avoid ResourceWarning
                process.stdin.close()
                process.stdout.close()
                process.stderr.close()
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    unittest.main()
