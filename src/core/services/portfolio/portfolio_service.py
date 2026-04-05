from src.core.primitives.portfolio import PortfolioContext, Position

def get_portfolio_context(session_id: str) -> PortfolioContext:
    """
    Retrieves a thin immutable snapshot of the portfolio context.
    Phase 3: Stub implementation.
    """
    # TODO (Jac): BEGIN – replace with walker call to query graph state
    return PortfolioContext(
        portfolio_id=f"port-{session_id}",
        total_value=10000.0,
        positions=[
            Position(symbol="META", quantity=10, avg_cost_basis=450.0, unrealized_pnl=500.0, weight_pct=0.45),
            Position(symbol="PLTR", quantity=100, avg_cost_basis=20.0, unrealized_pnl=400.0, weight_pct=0.24),
            Position(symbol="SPY", quantity=6, avg_cost_basis=500.0, unrealized_pnl=120.0, weight_pct=0.31)
        ]
    )
    # TODO (Jac): END
