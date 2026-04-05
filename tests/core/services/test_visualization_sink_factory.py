import unittest
from typing import Dict, Any
from src.core.services.visualization_sink_factory import VisualizationSinkFactory, VisualizationSinkFactoryError
from src.core.primitives.visualization_sink import VisualizationSink
from tests.utils import setup_test_logging

class MockLLMProvider:
    def generate_schema(self, prompt: str) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "nodes": {"type": "array"},
                "edges": {"type": "array"},
                "quant_summary": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "summary_text": {"type": "string"}
                    }
                }
            },
            "required": ["nodes", "edges", "quant_summary"]
        }

    def generate_insight_data(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "nodes": [
                {
                    "node_id": "n1", 
                    "schema": {"type": "ticker"}, 
                    "data": {"symbol": "AAPL", "name": "Apple"}
                },
                {
                    "node_id": "n2",
                    "schema": {"type": "generic"},
                    "data": {"status": "direct_data"}
                }
            ],
            "edges": [{"source_id": "n1", "target_id": "n2", "reasoning": "data link"}],
            "quant_summary": {"title": "Test Insight", "summary_text": "Validation works."}
        }

class TestVisualizationSinkFactory(unittest.TestCase):
    def setUp(self):
        setup_test_logging(self.id())

    def test_factory_create(self):
        llm = MockLLMProvider()
        sink = VisualizationSinkFactory.create("Analyze AAPL", llm) # type: ignore
        
        self.assertIsInstance(sink, VisualizationSink)
        self.assertEqual(len(sink.nodes), 2)
        self.assertEqual(len(sink.edges), 1)
        
        node2 = sink.nodes[1]
        self.assertEqual(node2.data["status"], "direct_data")

    def test_factory_validation_failure(self):
        class BadLLM:
            def generate_schema(self, p): return {"type": "object", "properties": {"nodes": {"type": "integer"}}}
            def generate_insight_data(self, p, s): return {"nodes": "not an integer"}
        
        with self.assertRaises(VisualizationSinkFactoryError):
            VisualizationSinkFactory.create("bad", BadLLM()) # type: ignore

if __name__ == "__main__":
    unittest.main()
