import unittest
import json
from pathlib import Path
from src.core.primitives.financial_insight import InsightNode, InsightEdge, QuantSummary
from src.core.primitives.visualization_sink import VisualizationSink
from src.core.primitives.ticker import Ticker
from src.core.primitives.portfolio import Portfolio
from tests.utils import setup_test_logging

class TestPrimitives(unittest.TestCase):
    def setUp(self):
        setup_test_logging(self.id())
    def test_insight_node_serialization(self) -> None:
        node = InsightNode(
            node_id="test-node",
            schema={"type": "ticker"},
            data={"symbol": "AAPL", "price": 150.0}
        )
        as_dict = node.to_dict()
        self.assertEqual(as_dict["node_id"], "test-node")
        self.assertEqual(as_dict["data"]["symbol"], "AAPL")
        
        reconstructed = InsightNode.from_dict(as_dict)
        self.assertEqual(reconstructed, node)

    def test_quant_summary_serialization(self) -> None:
        summary = QuantSummary(
            title="Analysis",
            summary_text="Text content",
            key_metrics={"P/E": 20}
        )
        as_dict = summary.to_dict()
        self.assertEqual(as_dict["title"], "Analysis")
        
        reconstructed = QuantSummary.from_dict(as_dict)
        self.assertEqual(reconstructed, summary)

    def test_visualization_sink_serialization(self) -> None:
        summary = QuantSummary(title="T", summary_text="S")
        node = InsightNode(node_id="n1", schema={}, data={})
        sink = VisualizationSink(
            insight_id="id-1",
            prompt="test prompt",
            created_at="2026-04-05T00:00:00Z",
            quant_summary=summary,
            nodes=(node,),
            root_node_id="n1"
        )
        as_dict = sink.to_dict()
        self.assertEqual(as_dict["insight_id"], "id-1")
        self.assertEqual(len(as_dict["nodes"]), 1)
        self.assertEqual(as_dict["quant_summary"]["title"], "T")
        
        reconstructed = VisualizationSink.from_dict(as_dict)
        self.assertEqual(reconstructed, sink)

    def test_ticker_portfolio_serialization(self) -> None:
        ticker = Ticker(symbol="MSFT", name="Microsoft")
        portfolio = Portfolio(id="port-1", tickers=[ticker])
        
        as_dict = portfolio.to_dict()
        self.assertEqual(as_dict["tickers"][0]["symbol"], "MSFT")
        
        reconstructed = Portfolio.from_dict(as_dict)
        self.assertEqual(reconstructed, portfolio)

    def test_immutability(self) -> None:
        """Verify frozen=True behavior for primitives."""
        node = InsightNode(node_id="n1", schema={}, data={})
        with self.assertRaises(Exception):
            node.node_id = "n2"  # type: ignore

        sink = VisualizationSink(
            insight_id="id-1", prompt="p", created_at="now", 
            quant_summary=QuantSummary("T", "S")
        )
        with self.assertRaises(Exception):
            sink.insight_id = "id-2"  # type: ignore

    def test_load_all_synthdata(self) -> None:
        """Validate loading all eight synthetic data files and their immutability."""
        synth_dir = Path("data/raw/synthetic_visualization_sinks")
        # Original four: 1, 2, 4, 5. New four: 6, 7, 8, 9.
        for i in [1, 2, 4, 5, 6, 7, 8, 9]:
            file_path = synth_dir / f"synthdata{i}.json"
            if not file_path.exists():
                print(f"Skipping {file_path} (not found)")
                continue
            
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Load from dict
            sink = VisualizationSink.from_dict(data)
            self.assertIsInstance(sink, VisualizationSink)
            
            # Verify basic fields
            self.assertEqual(sink.insight_id, data.get("insight_id") or data.get("node_id"))
            self.assertEqual(len(sink.nodes), len(data.get("nodes", [])))
            self.assertEqual(len(sink.edges), len(data.get("edges", [])))
            
            # Verify edge field flexibility (source / source_node_id, target / target_node_id, insight / insight_text)
            for j, orig_edge in enumerate(data.get("edges", [])):
                sink_edge = sink.edges[j]
                orig_source = orig_edge.get("source_id") or orig_edge.get("source") or orig_edge.get("source_node_id")
                orig_target = orig_edge.get("target_id") or orig_edge.get("target") or orig_edge.get("target_node_id")
                orig_reasoning = orig_edge.get("reasoning") or orig_edge.get("insight") or orig_edge.get("insight_text")
                
                self.assertEqual(sink_edge.source_id, orig_source)
                self.assertEqual(sink_edge.target_id, orig_target)
                self.assertEqual(sink_edge.reasoning, orig_reasoning)
            
            # Verify complex data preservation (structural references in data)
            if sink.nodes:
                orig_node = data["nodes"][0]
                self.assertEqual(sink.nodes[0].data, orig_node.get("data"))
            
            # Verify immutability
            with self.assertRaises(Exception):
                sink.nodes[0] = InsightNode("hack", {}, {}) # type: ignore

if __name__ == "__main__":
    unittest.main()
