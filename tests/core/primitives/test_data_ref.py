import unittest
from src.core.primitives.data_ref import DataRef
from src.core.primitives.financial_insight import InsightNode
from tests.utils import setup_test_logging

class TestDataRef(unittest.TestCase):
    def setUp(self):
        setup_test_logging(self.id())

    def test_data_ref_serialization(self):
        data_ref = DataRef(
            path="data/prices.csv",
            reader_name="csv_reader",
            format="csv",
            params={"header": True}
        )
        as_dict = data_ref.to_dict()
        self.assertEqual(as_dict["path"], "data/prices.csv")
        self.assertEqual(as_dict["reader_name"], "csv_reader")
        self.assertEqual(as_dict["params"]["header"], True)

        # Round trip
        back = DataRef.from_dict(as_dict)
        self.assertEqual(data_ref, back)

    def test_insight_node_with_data_ref(self):
        data_ref = DataRef(path="test.csv", reader_name="test_reader", format="csv")
        node = InsightNode(
            node_id="n1",
            schema={"type": "data_ref"},
            data=data_ref
        )
        
        as_dict = node.to_dict()
        self.assertEqual(as_dict["data"]["path"], "test.csv")
        
        # from_dict should reconstruct DataRef if it sees path/reader_name
        back = InsightNode.from_dict(as_dict)
        self.assertIsInstance(back.data, DataRef)
        self.assertEqual(back.data.path, "test.csv")

    def test_immutability(self):
        data_ref = DataRef(path="a", reader_name="b", format="c")
        with self.assertRaises(Exception):
            data_ref.path = "new" # type: ignore

if __name__ == "__main__":
    unittest.main()
