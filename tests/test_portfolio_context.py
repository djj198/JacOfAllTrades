from src.core.primitives.portfolio import PortfolioContext, Position, Fundamentals

def test_portfolio_context_roundtrip():
    fundamentals = Fundamentals(
        pe_ratio=25.5,
        market_cap_billions=1200.0,
        dividend_yield=0.012,
        eps_growth_next_year=0.15
    )
    
    pos1 = Position(
        symbol="AAPL",
        quantity=10.0,
        avg_cost_basis=150.0,
        unrealized_pnl=200.0,
        weight_pct=0.5,
        fundamentals=fundamentals
    )
    
    pos2 = Position(
        symbol="MSFT",
        quantity=5.0,
        avg_cost_basis=300.0,
        unrealized_pnl=100.0,
        weight_pct=0.5,
        fundamentals=None
    )
    
    ctx = PortfolioContext(
        portfolio_id="test-portfolio-123",
        total_value=3200.0,
        positions=[pos1, pos2]
    )
    
    # Convert to dict
    data = ctx.to_dict()
    assert data["portfolio_id"] == "test-portfolio-123"
    assert len(data["positions"]) == 2
    assert data["positions"][0]["fundamentals"]["pe_ratio"] == 25.5
    
    # Convert back to object
    ctx_back = PortfolioContext.from_dict(data)
    
    # Assert equality
    assert ctx == ctx_back
    assert ctx_back.positions[0].fundamentals.pe_ratio == 25.5
    assert ctx_back.positions[1].fundamentals is None

if __name__ == "__main__":
    test_portfolio_context_roundtrip()
    print("test_portfolio_context_roundtrip passed!")
