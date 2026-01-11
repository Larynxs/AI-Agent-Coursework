"""
Leverage Ratios Module
Calculates: Debt-to-Equity, Debt-to-Assets, Equity Multiplier, Interest Coverage, Cash Flow to Debt
"""

import pandas as pd
import numpy as np


class LeverageAnalysis:
    """Analyses company leverage and solvency."""
    
    def __init__(self, income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame = None):
        self.income_stmt = income_stmt
        self.balance_sheet = balance_sheet
        self.cash_flow = cash_flow
        self.ratios = {}
    
    def get_debt_to_equity(self) -> pd.Series:
        """Total Debt / Stockholders Equity"""
        try:
            result = self.balance_sheet.loc['Total Debt'] / self.balance_sheet.loc['Stockholders Equity']
            self.ratios['debt_to_equity'] = result
            return result
        except KeyError as e:
            print(f"  Error calculating debt-to-equity: {e}")
            return None
    
    def get_debt_to_assets(self) -> pd.Series:
        """Total Debt / Total Assets"""
        try:
            result = self.balance_sheet.loc['Total Debt'] / self.balance_sheet.loc['Total Assets']
            self.ratios['debt_to_assets'] = result
            return result
        except KeyError as e:
            print(f"  Error calculating debt-to-assets: {e}")
            return None
    
    def get_equity_multiplier(self) -> pd.Series:
        """Total Assets / Stockholders Equity"""
        try:
            result = self.balance_sheet.loc['Total Assets'] / self.balance_sheet.loc['Stockholders Equity']
            self.ratios['equity_multiplier'] = result
            return result
        except KeyError as e:
            print(f"  Error calculating equity multiplier: {e}")
            return None
    
    def get_interest_coverage(self) -> pd.Series:
        """EBIT / Interest Expense"""
        try:
            result = self.income_stmt.loc['EBIT'] / abs(self.income_stmt.loc['Interest Expense'])
            self.ratios['interest_coverage'] = result
            return result
        except KeyError as e:
            print(f"  Error calculating interest coverage: {e}")
            return None
    
    def get_cash_flow_to_debt(self) -> pd.Series:
        """Operating Cash Flow / Total Debt"""
        if self.cash_flow is None:
            return None
        try:
            result = self.cash_flow.loc['Operating Cash Flow'] / self.balance_sheet.loc['Total Debt']
            self.ratios['cash_flow_to_debt'] = result
            return result
        except KeyError as e:
            print(f"  Error calculating cash flow to debt: {e}")
            return None
    
    def calculate_all(self) -> dict:
        """Calculate all leverage ratios."""
        self.get_debt_to_equity()
        self.get_debt_to_assets()
        self.get_equity_multiplier()
        self.get_interest_coverage()
        self.get_cash_flow_to_debt()
        return self.ratios
    
    def get_latest_values(self) -> dict:
        """Get most recent year's values."""
        return {name: series.iloc[0] for name, series in self.ratios.items() if series is not None}
    
    def print_summary(self):
        """Print formatted summary."""
        if not self.ratios:
            print("No ratios calculated. Run calculate_all() first.")
            return
        
        print("\n" + "=" * 67)
        print("LEVERAGE ANALYSIS")
        print("=" * 67)
        
        years = list(self.ratios.values())[0].index.tolist()
        
        # Header
        header = f"{'Metric':<25}"
        for year in years[:5]:
            header += f"{str(year)[:4]:>12}"
        print(header)
        print("-" * 67)
        
        # Data rows
        display_names = {
            'debt_to_equity': 'Debt-to-Equity',
            'debt_to_assets': 'Debt-to-Assets',
            'equity_multiplier': 'Equity Multiplier',
            'interest_coverage': 'Interest Coverage',
            'cash_flow_to_debt': 'Cash Flow to Debt'
        }
        
        for key, name in display_names.items():
            if key in self.ratios and self.ratios[key] is not None:
                row = f"{name:<25}"
                for i in range(min(5, len(years))):
                    val = self.ratios[key].iloc[i]
                    row += f"{val:>12.2f}" if pd.notna(val) else f"{'N/A':>12}"
                print(row)
        
        print("-" * 67)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert ratios to DataFrame."""
        valid = {k: v for k, v in self.ratios.items() if v is not None}
        return pd.DataFrame(valid).T


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    import os
    
    paths = ["../APPL_Data/", "APPL_Data/", ""]
    data_dir = next((p for p in paths if os.path.exists(f"{p}AAPL_balance_sheet.csv")), None)
    
    if data_dir is not None:
        print("Testing Leverage Analysis...\n")
        
        income_stmt = pd.read_csv(f"{data_dir}AAPL_income_statement.csv", index_col=0)
        balance_sheet = pd.read_csv(f"{data_dir}AAPL_balance_sheet.csv", index_col=0)
        cash_flow = pd.read_csv(f"{data_dir}AAPL_cash_flow.csv", index_col=0)
        
        analysis = LeverageAnalysis(income_stmt, balance_sheet, cash_flow)
        analysis.calculate_all()
        analysis.print_summary()
        
        print("\n✅ Test passed!")
    else:
        print("No test data found. Place AAPL CSVs in APPL_Data/ folder.")