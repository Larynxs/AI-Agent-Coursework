"""
Profitability Ratios Module
===========================
Calculates profitability metrics to assess how effectively
a company generates profits from its operations.

Ratios Included:
    - Gross Margin
    - Operating Margin
    - Net Margin
    - Return on Equity (ROE)
    - Return on Assets (ROA)
"""

import pandas as pd
import numpy as np


class ProfitabilityAnalysis:
    """
    Analyses company profitability using key financial ratios.
    
    Profitability ratios measure how well a company converts
    revenue into profits at various stages of operations.
    
    Attributes:
        income_stmt (DataFrame): Income statement data
        balance_sheet (DataFrame): Balance sheet data
        ratios (dict): Calculated profitability ratios
    
    Example:
        >>> profitability = ProfitabilityAnalysis(income_stmt, balance_sheet)
        >>> results = profitability.calculate_all()
        >>> profitability.print_summary()
    """
    
    def __init__(self, income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame):
        """
        Initialise with financial statement data.
        
        Args:
            income_stmt: Income statement DataFrame with years as columns
            balance_sheet: Balance sheet DataFrame with years as columns
        """
        self.income_stmt = income_stmt
        self.balance_sheet = balance_sheet
        self.ratios = {}
    
    # =========================================================================
    # Individual Ratio Calculations
    # =========================================================================
    
    def get_gross_margin(self) -> pd.Series:
        """
        Calculate Gross Profit Margin.
        
        Formula: (Gross Profit / Total Revenue) × 100
        
        Interpretation:
            - Measures production efficiency
            - Higher is better (more profit per sale)
            - Industry-dependent benchmark
        
        Returns:
            Series of gross margin percentages by year
        """
        try:
            revenue = self.income_stmt.loc['Total Revenue']
            gross_profit = self.income_stmt.loc['Gross Profit']
            
            gross_margin = (gross_profit / revenue) * 100
            self.ratios['gross_margin'] = gross_margin
            return gross_margin
            
        except KeyError as e:
            print(f"  Error: Missing data field for gross margin - {e}")
            return None
    
    def get_operating_margin(self) -> pd.Series:
        """
        Calculate Operating Profit Margin.
        
        Formula: (Operating Income / Total Revenue) × 100
        
        Interpretation:
            - Measures operational efficiency
            - Shows profit after operating expenses
            - Excludes interest and taxes
        
        Returns:
            Series of operating margin percentages by year
        """
        try:
            revenue = self.income_stmt.loc['Total Revenue']
            operating_income = self.income_stmt.loc['Operating Income']
            
            operating_margin = (operating_income / revenue) * 100
            self.ratios['operating_margin'] = operating_margin
            return operating_margin
            
        except KeyError as e:
            print(f"  Error: Missing data field for operating margin - {e}")
            return None
    
    def get_net_margin(self) -> pd.Series:
        """
        Calculate Net Profit Margin.
        
        Formula: (Net Income / Total Revenue) × 100
        
        Interpretation:
            - Measures overall profitability
            - Shows profit after ALL expenses
            - Key metric for investors
        
        Returns:
            Series of net margin percentages by year
        """
        try:
            revenue = self.income_stmt.loc['Total Revenue']
            net_income = self.income_stmt.loc['Net Income']
            
            net_margin = (net_income / revenue) * 100
            self.ratios['net_margin'] = net_margin
            return net_margin
            
        except KeyError as e:
            print(f"  Error: Missing data field for net margin - {e}")
            return None
    
    def get_roe(self) -> pd.Series:
        """
        Calculate Return on Equity (ROE).
        
        Formula: (Net Income / Stockholders Equity) × 100
        
        Interpretation:
            - Measures return generated for shareholders
            - Higher ROE indicates efficient use of equity
            - Benchmark: >15% is generally good
        
        Returns:
            Series of ROE percentages by year
        """
        try:
            net_income = self.income_stmt.loc['Net Income']
            equity = self.balance_sheet.loc['Stockholders Equity']
            
            roe = (net_income / equity) * 100
            self.ratios['roe'] = roe
            return roe
            
        except KeyError as e:
            print(f"  Error: Missing data field for ROE - {e}")
            return None
    
    def get_roa(self) -> pd.Series:
        """
        Calculate Return on Assets (ROA).
        
        Formula: (Net Income / Total Assets) × 100
        
        Interpretation:
            - Measures efficiency of asset utilisation
            - Shows profit generated per dollar of assets
            - Benchmark: >5% is generally acceptable
        
        Returns:
            Series of ROA percentages by year
        """
        try:
            net_income = self.income_stmt.loc['Net Income']
            total_assets = self.balance_sheet.loc['Total Assets']
            
            roa = (net_income / total_assets) * 100
            self.ratios['roa'] = roa
            return roa
            
        except KeyError as e:
            print(f"  Error: Missing data field for ROA - {e}")
            return None
    
    # =========================================================================
    # Aggregate Functions
    # =========================================================================
    
    def calculate_all(self) -> dict:
        """
        Calculate all profitability ratios.
        
        Returns:
            Dictionary containing all profitability metrics
        """
        print("Calculating profitability ratios...")
        
        self.get_gross_margin()
        self.get_operating_margin()
        self.get_net_margin()
        self.get_roe()
        self.get_roa()
        
        print(f"  Completed: {len(self.ratios)} ratios calculated")
        return self.ratios
    
    def get_latest_values(self) -> dict:
        """
        Get the most recent year's values for all ratios.
        
        Returns:
            Dictionary with ratio names and latest values
        """
        latest = {}
        for name, series in self.ratios.items():
            if series is not None and len(series) > 0:
                latest[name] = series.iloc[0]  # First column is most recent
        return latest
    
    def print_summary(self):
        """Print a formatted summary of profitability ratios."""
        if not self.ratios:
            print("No ratios calculated. Run calculate_all() first.")
            return
        
        print("\n" + "=" * 55)
        print("PROFITABILITY ANALYSIS")
        print("=" * 55)
        
        # Get years from first available ratio
        years = None
        for ratio in self.ratios.values():
            if ratio is not None:
                years = ratio.index.tolist()
                break
        
        if years is None:
            print("No data available")
            return
        
        # Print header
        header = f"{'Metric':<25}"
        for year in years[:4]:  # Show up to 4 years
            # Extract just the year part
            year_str = str(year)[:4] if len(str(year)) >= 4 else str(year)
            header += f"{year_str:>12}"
        print(header)
        print("-" * 55)
        
        # Print each ratio
        ratio_display_names = {
            'gross_margin': 'Gross Margin (%)',
            'operating_margin': 'Operating Margin (%)',
            'net_margin': 'Net Margin (%)',
            'roe': 'Return on Equity (%)',
            'roa': 'Return on Assets (%)'
        }
        
        for key, display_name in ratio_display_names.items():
            if key in self.ratios and self.ratios[key] is not None:
                row = f"{display_name:<25}"
                for i, year in enumerate(years[:4]):
                    value = self.ratios[key].iloc[i]
                    row += f"{value:>12.2f}"
                print(row)
            else:
                print(f"{display_name:<25}{'N/A':>12}")
        
        print("-" * 55)
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert all ratios to a single DataFrame.
        
        Returns:
            DataFrame with ratios as rows and years as columns
        """
        if not self.ratios:
            return pd.DataFrame()
        
        # Filter out None values and create DataFrame
        valid_ratios = {k: v for k, v in self.ratios.items() if v is not None}
        return pd.DataFrame(valid_ratios).T


# =============================================================================
# Standalone Functions (for direct use without class)
# =============================================================================

def calculate_gross_margin(income_stmt: pd.DataFrame) -> pd.Series:
    """Calculate Gross Margin from income statement."""
    revenue = income_stmt.loc['Total Revenue']
    gross_profit = income_stmt.loc['Gross Profit']
    return (gross_profit / revenue) * 100


def calculate_operating_margin(income_stmt: pd.DataFrame) -> pd.Series:
    """Calculate Operating Margin from income statement."""
    revenue = income_stmt.loc['Total Revenue']
    operating_income = income_stmt.loc['Operating Income']
    return (operating_income / revenue) * 100


def calculate_net_margin(income_stmt: pd.DataFrame) -> pd.Series:
    """Calculate Net Margin from income statement."""
    revenue = income_stmt.loc['Total Revenue']
    net_income = income_stmt.loc['Net Income']
    return (net_income / revenue) * 100


def calculate_roe(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> pd.Series:
    """Calculate Return on Equity."""
    net_income = income_stmt.loc['Net Income']
    equity = balance_sheet.loc['Stockholders Equity']
    return (net_income / equity) * 100


def calculate_roa(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> pd.Series:
    """Calculate Return on Assets."""
    net_income = income_stmt.loc['Net Income']
    total_assets = balance_sheet.loc['Total Assets']
    return (net_income / total_assets) * 100


# =============================================================================
# Main - Test the module
# =============================================================================

if __name__ == "__main__":
    # Test with sample data
    print("Profitability Analysis Module")
    print("Run this with actual financial data to see results.")
    print("\nExample usage:")
    print("  from ratios.profitability import ProfitabilityAnalysis")
    print("  analysis = ProfitabilityAnalysis(income_stmt, balance_sheet)")
    print("  results = analysis.calculate_all()")
    print("  analysis.print_summary()")