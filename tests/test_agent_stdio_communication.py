import subprocess
import json
import sys
import os
import time
import unittest
from pathlib import Path
from typing import Any, Dict
from tests.utils import setup_test_logging

class TestAgentACPStability(unittest.TestCase):
    def setUp(self):
        self.project_root = "/home/theodoric/DataspellProjects/JacOfAllTrades"
        self.main_path = os.path.join(self.project_root, "main.py")
        self.log_path = setup_test_logging(self.id())
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = self.project_root
        self.env["DEBUG_TRANSPORT"] = "true"
        self.env["AGENT_LOG_PATH"] = self.log_path
        
        # New prompts for rotation
        self.test_prompts = [
            "Perform a complete portfolio risk assessment for my holdings in META, PLTR, and SPY",
            "Deep dive on META fundamentals, recent price history impact on my position",
            "Suggest portfolio rebalancing for META, PLTR, SPY",
            "Compare META and PLTR fundamentals and position performance"
        ]
        
        # Expected synthdata files corresponding to prompts
        self.synth_files = [
            "synthdata6.json",
            "synthdata7.json",
            "synthdata8.json",
            "synthdata9.json"
        ]

    def _read_logs(self):
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                return f.read()
        return ""

    def test_agent_stdio_stability_cycles(self):
        """
        Open-loop stability test:
        - 10 cycles of initialize -> session/new -> session/prompt
        - Rotates through 4 sophisticated synthdata prompts
        """
        # Clear logs
        if os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                f.write("")

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
            for cycle in range(10):
                prompt_text = self.test_prompts[cycle % len(self.test_prompts)]
                expected_file = self.synth_files[cycle % len(self.synth_files)]
                
                print(f"Cycle {cycle+1}/10 - Prompt: {prompt_text[:40]}...")

                # 1. initialize
                req_id = cycle * 10 + 1
                init_req = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "method": "initialize",
                    "params": {
                        "protocol_version": 1,
                        "agent_info": {"name": "stability-tester", "version": "1.0.0"}
                    }
                }
                process.stdin.write(json.dumps(init_req) + "\n")
                process.stdin.flush()
                
                line = process.stdout.readline()
                self.assertTrue(line, "No response during initialize")
                res = json.loads(line)
                self.assertEqual(res.get("id"), req_id)

                # 2. session/new
                req_id = cycle * 10 + 2
                session_req = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "method": "session/new",
                    "params": {
                        "cwd": self.project_root,
                        "mcpServers": []
                    }
                }
                process.stdin.write(json.dumps(session_req) + "\n")
                process.stdin.flush()
                
                line = process.stdout.readline()
                self.assertTrue(line, "No response during session/new")
                res = json.loads(line)
                self.assertEqual(res.get("id"), req_id)
                
                # Capture the session_id from the response
                session_id = res["result"]["sessionId"]

                # 3. session/prompt
                req_id = cycle * 10 + 3
                prompt_req = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "method": "session/prompt",
                    "params": {
                        "prompt": [{"type": "text", "text": prompt_text}],
                        "sessionId": session_id
                    }
                }
                
                start_time = time.time()
                process.stdin.write(json.dumps(prompt_req) + "\n")
                process.stdin.flush()

                final_res = None
                while True:
                    line = process.stdout.readline()
                    if not line: break
                    res = json.loads(line)
                    if res.get("id") == req_id:
                        final_res = res
                        break
                    # Monitor for errors in notifications
                    if "error" in res:
                        self.fail(f"SDK error notification: {res}")

                latency_ms = (time.time() - start_time) * 1000
                self.assertIsNotNone(final_res, "PromptResponse missing")
                
                # Validation of VisualizationSink
                result = final_res.get("result", {})
                meta = result.get("_meta", {})
                sink_data = meta.get("visualization_sink")
                self.assertIsNotNone(sink_data, "visualization_sink missing in _meta")
                
                # Load expected data for comparison
                expected_path = Path(self.project_root) / "data/raw/synthetic_visualization_sinks" / expected_file
                with open(expected_path, "r") as f:
                    expected_data = json.load(f)
                
                # Validate key structure matches expected synthdata
                self.assertEqual(sink_data["insight_id"], expected_data["insight_id"])
                self.assertEqual(len(sink_data["nodes"]), len(expected_data["nodes"]))
                self.assertEqual(len(sink_data["edges"]), len(expected_data.get("edges", [])))
                self.assertEqual(sink_data["visualizer_pseudo_prompt"], expected_data["visualizer_pseudo_prompt"])

                # Check logs and stderr for background errors
                logs = self._read_logs()
                stderr_content = ""
                # We can't easily read stderr without blocking, but we can check if it's closed or has data
                # Since we are using subprocess.PIPE, we can use a non-blocking read or check it at the end.
                # For now, we mainly check logs where SDK errors are reported.
                for err in ["Invalid params", "Internal error", "Background task failed", "ResourceWarning"]:
                    if err in logs:
                        print(f"ERROR/WARNING FOUND IN LOGS: {err}")
                        self.fail(f"Found '{err}' in agent logs")

            print("\nStability test passed: 10/10 cycles clean.")

        finally:
            process.terminate()
            process.stdin.close()
            process.stdout.close()
            process.stderr.close()
            process.wait()

if __name__ == "__main__":
    unittest.main()
