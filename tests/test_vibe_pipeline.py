from src.agent.handlers import JacPromptHandler
from src.interfaces.protocols import PromptInput

def test_full_vibe_pipeline():
    # Prompt matches synthdata6 mapping
    input_data = PromptInput(prompt="Perform a complete portfolio risk assessment for META, PLTR, and SPY", session_id="test-123")
    handler = JacPromptHandler()
    output = handler.handle_prompt(input_data)
    
    output_dict = output.to_dict()
    assert "visualization_sink" in output_dict
    assert output_dict["visualization_sink"]["nodes"]  # must contain real nodes from insight
    
    # Verify it loaded synthdata6 which has 3 nodes
    nodes = output_dict["visualization_sink"]["nodes"]
    assert len(nodes) == 3
    assert nodes[0]["node_id"] == "portfolio_structural_snapshot"
    
    print("test_full_vibe_pipeline passed!")

if __name__ == "__main__":
    test_full_vibe_pipeline()
