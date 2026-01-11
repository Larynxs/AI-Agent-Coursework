"""
Efficiency Ratios Module
Calculates: Asset Turnover
"""

import pandas as pd
import numpy as np


class EfficiencyAnalysis:
    """Analyses how efficiently a company uses its assets."""
    
    def __init__(self, income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame):
        self.income_stmt = income_stmt
        self.balance_sheet = balance_sheet
        self.ratios = {}
    
    def get_asset_turnover(self) -> pd.Series:
        """Total Revenue / Total Assets"""
        try:
            result = self.income_stmt.loc['Total Revenue'] / self.balance_sheet.loc['Total Assets']
            self.ratios['asset_turnover'] = result
            return result
        except KeyError as e:
            print(f"  Error calculating asset turnover: {e}")
            return None
    
    def calculate_all(self) -> dict:
        """Calculate all efficiency ratios."""
        self.get_asset_turnover()
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
        print("EFFICIENCY ANALYSIS")
        print("=" * 67)
        
        years = list(self.ratios.values())[0].index.tolist()
        
        header = f"{'Metric':<25}"
        for year in years[:5]:
            header += f"{str(year)[:4]:>12}"
        print(header)
        print("-" * 67)
        
        display_names = {'asset_turnover': 'Asset Turnover'}
        
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
        print("Testing Efficiency Analysis...\n")
        
        income_stmt = pd.read_csv(f"{data_dir}AAPL_income_statement.csv", index_col=0)
        balance_sheet = pd.read_csv(f"{data_dir}AAPL_balance_sheet.csv", index_col=0)
        
        analysis = EfficiencyAnalysis(income_stmt, balance_sheet)
        analysis.calculate_all()
        analysis.print_summary()
        
        print("\n✅ Test passed!")
    else:
        print("No test data found. Place AAPL CSVs in APPL_Data/ folder.")