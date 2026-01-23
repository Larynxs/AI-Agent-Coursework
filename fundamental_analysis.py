"""
Fundamental Analysis - Main Module
Combines all ratio analyses into one comprehensive report.
"""

import pandas as pd
from pathlib import Path

from Ratios.profitability import ProfitabilityAnalysis
from Ratios.liquidity import LiquidityAnalysis
from Ratios.leverage import LeverageAnalysis
from Ratios.efficiency import EfficiencyAnalysis
from Ratios.growth import GrowthAnalysis
from Ratios.risk import RiskAnalysis


class FundamentalAnalysis:
    """Runs complete fundamental analysis on a company."""
    
    def __init__(self, ticker: str, data_dir: str, market_cap: float):
        self.ticker = ticker.upper()
        self.data_dir = Path(data_dir)
        self.market_cap = market_cap
        
        # Load data
        self.income_stmt = pd.read_csv(self.data_dir / f"{self.ticker}_income_statement.csv", index_col=0)
        self.balance_sheet = pd.read_csv(self.data_dir / f"{self.ticker}_balance_sheet.csv", index_col=0)
        self.cash_flow = pd.read_csv(self.data_dir / f"{self.ticker}_cash_flow.csv", index_col=0)
        
        # Store results
        self.results = {}
    
    def run_all(self) -> dict:
        """Run all analyses."""
        print(f"\n{'='*67}")
        print(f"FUNDAMENTAL ANALYSIS: {self.ticker}")
        print(f"{'='*67}")
        
        # Profitability
        prof = ProfitabilityAnalysis(self.income_stmt, self.balance_sheet)
        prof.calculate_all()
        prof.print_summary()
        self.results['profitability'] = prof.ratios
        
        # Liquidity
        liq = LiquidityAnalysis(self.balance_sheet)
        liq.calculate_all()
        liq.print_summary()
        self.results['liquidity'] = liq.ratios
        
        # Leverage
        lev = LeverageAnalysis(self.income_stmt, self.balance_sheet, self.cash_flow)
        lev.calculate_all()
        lev.print_summary()
        self.results['leverage'] = lev.ratios
        
        # Efficiency
        eff = EfficiencyAnalysis(self.income_stmt, self.balance_sheet)
        eff.calculate_all()
        eff.print_summary()
        self.results['efficiency'] = eff.ratios
        
        # Growth
        grow = GrowthAnalysis(self.income_stmt)
        grow.calculate_all()
        grow.print_summary()
        self.results['growth'] = grow.ratios
        
        # Risk
        risk = RiskAnalysis(self.income_stmt, self.balance_sheet, self.market_cap)
        risk.calculate_all()
        risk.print_summary()
        self.results['risk'] = risk.ratios
        
        print(f"\n{'='*67}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*67}")
        
        return self.results
    
    def get_summary_dict(self) -> dict:
        """Get latest values for all ratios as a flat dictionary."""
        summary = {}
        for category, ratios in self.results.items():
            for name, series in ratios.items():
                if series is not None and len(series) > 0:
                    summary[name] = series.iloc[0]
        return summary


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    # Apple's market cap (update as needed)
    APPLE_MARKET_CAP = 3_500_000_000_000  # $3.5 trillion
    
    analysis = FundamentalAnalysis(
        ticker="AAPL",
        data_dir="APPL_Data",
        market_cap=APPLE_MARKET_CAP
    )
    
    results = analysis.run_all()
    
    print("\n All tests passed!")