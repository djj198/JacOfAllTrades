from src.core.services.financial_insight import create_financial_insight
from src.core.primitives.financial_insight import FinancialInsight

def test_create_financial_insight_risk_assessment():
    prompt = "Perform a complete portfolio risk assessment for META, PLTR, and SPY"
    insight = create_financial_insight(prompt)
    
    assert isinstance(insight, FinancialInsight)
    assert insight.prompt == prompt
    # synthdata6.json has insight_id "vis_portfolio_risk_full_20260405"
    assert insight.insight_id == "vis_portfolio_risk_full_20260405"
    assert len(insight.nodes) > 0
    assert insight.quant_summary.title == "Portfolio Risk Snapshot"

def test_create_financial_insight_deep_dive():
    prompt = "Deep dive on META fundamentals"
    insight = create_financial_insight(prompt)
    
    # Matches "DEEP DIVE" in prompt_upper and "META" in prompt_upper
    assert insight.insight_id == "vis_meta_deep_dive_20260405"
    assert any(n.node_id == "meta_structural_ticker" for n in insight.nodes)

def test_create_financial_insight_fallback():
    prompt = "Something completely different"
    insight = create_financial_insight(prompt)
    
    assert insight.quant_summary.title == "Generic Insight"
    assert len(insight.nodes) == 1
    assert insight.nodes[0].node_id == "root"

if __name__ == "__main__":
    test_create_financial_insight_risk_assessment()
    test_create_financial_insight_deep_dive()
    test_create_financial_insight_fallback()
    print("test_financial_insight_service passed!")
