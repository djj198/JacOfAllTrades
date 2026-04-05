import uuid
from datetime import datetime, timezone
from src.core.primitives.visualization_sink import VisualizationSink
from src.core.primitives.financial_insight import InsightNode, InsightEdge, QuantSummary

def create_visualization_sink(prompt: str) -> VisualizationSink:
    insight_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    # Realistic stub generation based on prompt text
    prompt_upper = prompt.upper()
    
    nodes = []
    edges = []
    root_node_id = "root"
    
    if "META" in prompt_upper:
        nodes.append(InsightNode(
            node_id="root",
            schema={"type": "ticker_info"},
            data={"symbol": "META", "price": 490.23, "change": "+1.2%"}
        ))
        quant_summary = QuantSummary(
            title="META Analysis",
            summary_text="Meta shows strong correlation with social media trends.",
            key_metrics={"P/E": 25.4, "Volume": "12M"}
        )
        visualizer_pseudo_prompt = "Draw a bull-eye chart centered on META's current valuation."
        suggested_chart_types = ["annotated_line"]
    elif "S&P" in prompt_upper or "SPY" in prompt_upper:
        nodes.append(InsightNode(
            node_id="root",
            schema={"type": "index_info"},
            data={"name": "S&P 500", "value": 5200.45, "trend": "Bullish"}
        ))
        quant_summary = QuantSummary(
            title="S&P 500 Market Insight",
            summary_text="Overall market sentiment is positive following recent earnings.",
            key_metrics={"RSI": 62, "MACD": "Strong Buy"}
        )
        visualizer_pseudo_prompt = "Render a heatmap of S&P 500 sectors."
        suggested_chart_types = ["heatmap"]
    else:
        nodes.append(InsightNode(
            node_id="root",
            schema={"type": "generic_insight"},
            data={"topic": "General Market", "status": "Stable"}
        ))
        quant_summary = QuantSummary(
            title="General Market Overview",
            summary_text="Generic market data analysis.",
            key_metrics={"Volatility": "Low"}
        )
        visualizer_pseudo_prompt = "Show a network graph of related financial entities."
        suggested_chart_types = ["network_graph"]

    return VisualizationSink(
        insight_id=insight_id,
        prompt=prompt,
        created_at=created_at,
        quant_summary=quant_summary,
        nodes=nodes,
        edges=edges,
        root_node_id=root_node_id,
        visualizer_pseudo_prompt=visualizer_pseudo_prompt,
        suggested_chart_types=suggested_chart_types
    )
