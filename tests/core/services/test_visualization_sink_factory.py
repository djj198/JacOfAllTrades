import unittest
from typing import Dict, Any
from src.core.services.visualization_sink_factory import VisualizationSinkFactory, VisualizationSinkFactoryError
from src.core.primitives.visualization_sink import VisualizationSink
from src.core.primitives.data_ref import DataRef
from src.core.services.shared.readers.safe_lambda_readers import SafeLambdaReaderRegistry
from tests.utils import setup_test_logging

class MockLLMProvider:
    def generate_schema(self, prompt: str) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "nodes": {"type": "array"},
                "edges": {"type": "array"},
                "summary": {"type": "object"}
            },
            "required": ["nodes", "edges", "summary"]
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
                    "schema": {"type": "data_ref"},
                    "data": {
                        "path": "test.csv", 
                        "reader_name": "csv_timeseries_lazy", 
                        "format": "csv"
                    }
                }
            ],
            "edges": [{"source_id": "n1", "target_id": "n2", "reasoning": "data link"}],
            "summary": {"title": "Test Insight", "summary_text": "Validation works."}
        }

class TestVisualizationSinkFactory(unittest.TestCase):
    def setUp(self):
        setup_test_logging(self.id())

    def test_factory_create(self):
        llm = MockLLMProvider()
        sink = VisualizationSinkFactory.create("Analyze AAPL with CSV", llm) # type: ignore
        
        self.assertIsInstance(sink, VisualizationSink)
        self.assertEqual(len(sink.nodes), 2)
        self.assertEqual(len(sink.edges), 1)
        
        # Verify reader attachment
        node2 = sink.nodes[1]
        # Our reader returns {"status": "lazy_loaded", "path": "test.csv", "params": None}
        self.assertEqual(node2.data["status"], "lazy_loaded")
        self.assertEqual(node2.data["path"], "test.csv")

    def test_factory_validation_failure(self):
        class BadLLM:
            def generate_schema(self, p): return {"type": "object", "properties": {"nodes": {"type": "integer"}}}
            def generate_insight_data(self, p, s): return {"nodes": "not an integer"}
        
        with self.assertRaises(VisualizationSinkFactoryError):
            VisualizationSinkFactory.create("bad", BadLLM()) # type: ignore

if __name__ == "__main__":
    unittest.main()
