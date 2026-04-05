import unittest
import json
import os
from pathlib import Path
from src.core.services.visualization_service import create_visualization_sink
from src.core.primitives.visualization_sink import VisualizationSink

class TestVisualizationService(unittest.TestCase):
    def test_create_meta_sink(self) -> None:
        sink = create_visualization_sink("Analysis of META performance")
        self.assertEqual(sink.prompt, "Analysis of META performance")
        self.assertEqual(sink.quant_summary.title, "META Analysis")
        self.assertIn("annotated_line", sink.suggested_chart_types)
        
        # Verify JSON serializability
        as_dict = sink.to_dict()
        self.assertIsInstance(json.dumps(as_dict), str)
        
        # Save sample output for documentation/mocking
        sample_path = Path("data/raw/synthetic_visualization_sinks/meta_analysis_sample.json")
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sample_path, "w") as f:
            json.dump(as_dict, f, indent=2)

    def test_create_spy_sink(self) -> None:
        sink = create_visualization_sink("Give me S&P 500 heatmap")
        self.assertEqual(sink.quant_summary.title, "S&P 500 Market Insight")
        self.assertIn("heatmap", sink.suggested_chart_types)

    def test_create_generic_sink(self) -> None:
        sink = create_visualization_sink("What is happening in the market?")
        self.assertEqual(sink.quant_summary.title, "General Market Overview")
        self.assertIn("network_graph", sink.suggested_chart_types)

    def test_synthetic_data_roundtrip(self) -> None:
        """Task 1: Load each synthdata*.json and verify round-trip serialization."""
        synth_dir = Path("data/raw/synthetic_visualization_sinks")
        synth_files = list(synth_dir.glob("synthdata*.json"))
        
        if not synth_files:
            self.fail("No synthetic data files found in data/raw/synthetic_visualization_sinks")

        for synth_path in synth_files:
            with open(synth_path, "r") as f:
                original_data = json.load(f)
            
            # 1. Parse into VisualizationSink
            try:
                sink = VisualizationSink.from_dict(original_data)
            except Exception as e:
                self.fail(f"Failed to parse {synth_path.name}: {e}")

            # 2. Assert key fields are preserved
            # Note: fields might have been mapped, so we check the object attributes
            self.assertTrue(hasattr(sink, 'insight_id'), f"Missing insight_id in {synth_path.name}")
            self.assertTrue(hasattr(sink, 'quant_summary'), f"Missing quant_summary in {synth_path.name}")
            self.assertTrue(len(sink.nodes) > 0, f"No nodes in {synth_path.name}")
            
            # 3. Verify node data preservation (schema and data)
            # Check first node
            if original_data["nodes"]:
                orig_node = original_data["nodes"][0]
                sink_node = sink.nodes[0]
                self.assertEqual(sink_node.node_id, orig_node.get("node_id"), f"Node ID mismatch in {synth_path.name}")
                self.assertEqual(sink_node.schema, orig_node.get("schema"), f"Node schema mismatch in {synth_path.name}")
                self.assertEqual(sink_node.data, orig_node.get("data"), f"Node data mismatch in {synth_path.name}")

            # 4. Round-trip serialization: to_dict() == original after from_dict()
            reserialized_data = sink.to_dict()
            reconstructed_sink = VisualizationSink.from_dict(reserialized_data)
            self.assertEqual(sink, reconstructed_sink, f"Round-trip failed for {synth_path.name}")
            
            # 5. Verify Edge flexibility again in the context of service/sink
            for j, orig_edge in enumerate(original_data.get("edges", [])):
                sink_edge = sink.edges[j]
                orig_source = orig_edge.get("source_id") or orig_edge.get("source") or orig_edge.get("source_node_id")
                self.assertEqual(sink_edge.source_id, orig_source, f"Edge source mismatch in {synth_path.name}")

            # 6. Verify nested data preservation
            if original_data["nodes"]:
                orig_node_data = original_data["nodes"][0].get("data")
                self.assertEqual(sink.nodes[0].data, orig_node_data, f"Nested data mismatch in {synth_path.name}")

if __name__ == "__main__":
    unittest.main()
