import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundamentalCollector:
    """
    Collects financial statements and computes ratios for fundamental analysis.
    
    Supports any ticker on Yahoo Finance. Designed to be easily swappable
    between companies for flexible analysis.
    
    Example Usage:
        collector = FundamentalCollector("AAPL")
        statements = collector.get_all_statements()
        ratios = collector.compute_ratios()
        collector.export_for_llm("apple_analysis.json")
    """
    
    # Suggested companies from coursework brief
    SUGGESTED_TICKERS = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "unilever": "ULVR.L",
        "nestle": "NESN.SW",
        "rolls_royce": "RR.L",
        "siemens": "SIE.DE",
        "bp": "BP.L",
        "shell": "SHEL.L",
    }
    
    def __init__(self, ticker: str):
        """
        Initialize with a ticker symbol.
        
        Args:
            ticker: Stock symbol (e.g., "AAPL", "MSFT", "BP.L")
                   Or company name (e.g., "apple", "microsoft")
        """
        # Resolve friendly names to tickers
        self.ticker = self.SUGGESTED_TICKERS.get(ticker.lower(), ticker.upper())
        self.stock = yf.Ticker(self.ticker)
        self._info = None
        self._income_stmt = None
        self._balance_sheet = None
        self._cash_flow = None
        
        logger.info(f"Initialized FundamentalCollector for {self.ticker}")
    
    # =========================================================================
    # Company Info
    # =========================================================================
    
    @property
    def info(self) -> Dict:
        """Get company information."""
        if self._info is None:
            self._info = self.stock.info
        return self._info
    
    def get_company_profile(self) -> Dict:
        """Get a summary of company information."""
        info = self.info
        return {
            "ticker": self.ticker,
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "country": info.get("country", "N/A"),
            "currency": info.get("currency", "USD"),
            "market_cap": info.get("marketCap", 0),
            "employees": info.get("fullTimeEmployees", 0),
            "website": info.get("website", "N/A"),
            "description": info.get("longBusinessSummary", "N/A")[:500] + "...",
        }
    
    # =========================================================================
    # Financial Statements
    # =========================================================================
    
    def get_income_statement(self, quarterly: bool = False) -> pd.DataFrame:
        """
        Fetch income statement.
        
        Args:
            quarterly: If True, get quarterly data. Otherwise annual.
            
        Returns:
            DataFrame with income statement line items as rows, years as columns.
        """
        if quarterly:
            df = self.stock.quarterly_income_stmt
        else:
            df = self.stock.income_stmt
            
        self._income_stmt = df
        logger.info(f"Fetched income statement: {df.shape[1]} periods")
        return df
    
    def get_balance_sheet(self, quarterly: bool = False) -> pd.DataFrame:
        """
        Fetch balance sheet.
        
        Args:
            quarterly: If True, get quarterly data. Otherwise annual.
            
        Returns:
            DataFrame with balance sheet line items as rows, years as columns.
        """
        if quarterly:
            df = self.stock.quarterly_balance_sheet
        else:
            df = self.stock.balance_sheet
            
        self._balance_sheet = df
        logger.info(f"Fetched balance sheet: {df.shape[1]} periods")
        return df
    
    def get_cash_flow(self, quarterly: bool = False) -> pd.DataFrame:
        """
        Fetch cash flow statement.
        
        Args:
            quarterly: If True, get quarterly data. Otherwise annual.
            
        Returns:
            DataFrame with cash flow line items as rows, years as columns.
        """
        if quarterly:
            df = self.stock.quarterly_cashflow
        else:
            df = self.stock.cashflow
            
        self._cash_flow = df
        logger.info(f"Fetched cash flow statement: {df.shape[1]} periods")
        return df
    
    def get_all_statements(self, quarterly: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Fetch all three financial statements.
        
        Returns:
            Dictionary with 'income_statement', 'balance_sheet', 'cash_flow' keys.
        """
        return {
            "income_statement": self.get_income_statement(quarterly),
            "balance_sheet": self.get_balance_sheet(quarterly),
            "cash_flow": self.get_cash_flow(quarterly),
        }
    
    # =========================================================================
    # Key Metrics Extraction
    # =========================================================================
    
    def _safe_get(self, df: pd.DataFrame, keys: list, period: int = 0) -> float:
        """Safely extract a value from financial statement."""
        for key in keys:
            if key in df.index:
                val = df.iloc[:, period].get(key)
                if pd.notna(val):
                    return float(val)
        return np.nan
    
    def get_key_metrics(self) -> pd.DataFrame:
        """
        Extract key financial metrics across all available years.
        
        Returns:
            DataFrame with metrics as rows, years as columns.
        """
        # Ensure statements are loaded
        if self._income_stmt is None:
            self.get_income_statement()
        if self._balance_sheet is None:
            self.get_balance_sheet()
        if self._cash_flow is None:
            self.get_cash_flow()
        
        inc = self._income_stmt
        bal = self._balance_sheet
        cf = self._cash_flow
        
        # Get available periods (years)
        periods = inc.columns
        
        metrics = {}
        
        for i, period in enumerate(periods):
            year = period.year if hasattr(period, 'year') else str(period)
            
            metrics[year] = {
                # Income Statement Items
                "Revenue": self._safe_get(inc, ["Total Revenue", "Revenue"], i),
                "Gross Profit": self._safe_get(inc, ["Gross Profit"], i),
                "Operating Income": self._safe_get(inc, ["Operating Income", "EBIT"], i),
                "Net Income": self._safe_get(inc, ["Net Income", "Net Income Common Stockholders"], i),
                "EPS": self._safe_get(inc, ["Basic EPS", "Diluted EPS"], i),
                
                # Balance Sheet Items
                "Total Assets": self._safe_get(bal, ["Total Assets"], i),
                "Total Liabilities": self._safe_get(bal, ["Total Liabilities Net Minority Interest", "Total Liabilities"], i),
                "Total Equity": self._safe_get(bal, ["Total Equity Gross Minority Interest", "Stockholders Equity", "Total Stockholders Equity"], i),
                "Total Debt": self._safe_get(bal, ["Total Debt", "Long Term Debt"], i),
                "Cash": self._safe_get(bal, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"], i),
                "Current Assets": self._safe_get(bal, ["Current Assets"], i),
                "Current Liabilities": self._safe_get(bal, ["Current Liabilities"], i),
                
                # Cash Flow Items
                "Operating Cash Flow": self._safe_get(cf, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"], i),
                "Capital Expenditure": self._safe_get(cf, ["Capital Expenditure"], i),
                "Free Cash Flow": self._safe_get(cf, ["Free Cash Flow"], i),
                "Dividends Paid": self._safe_get(cf, ["Cash Dividends Paid", "Common Stock Dividend Paid"], i),
            }
        
        df = pd.DataFrame(metrics)
        # Sort columns (years) in descending order
        df = df[sorted(df.columns, reverse=True)]
        
        return df
    
    # =========================================================================
    # Financial Ratios
    # =========================================================================
    
    def compute_ratios(self) -> pd.DataFrame:
        """
        Compute key financial ratios for fundamental analysis.
        
        Categories:
        - Profitability Ratios
        - Leverage Ratios
        - Liquidity Ratios
        - Efficiency Ratios
        - Growth Rates
        
        Returns:
            DataFrame with ratios as rows, years as columns.
        """
        metrics = self.get_key_metrics()
        
        ratios = {}
        
        for year in metrics.columns:
            m = metrics[year]
            
            ratios[year] = {
                # === Profitability Ratios ===
                "Gross Margin (%)": self._pct(m["Gross Profit"], m["Revenue"]),
                "Operating Margin (%)": self._pct(m["Operating Income"], m["Revenue"]),
                "Net Profit Margin (%)": self._pct(m["Net Income"], m["Revenue"]),
                "ROE (%)": self._pct(m["Net Income"], m["Total Equity"]),
                "ROA (%)": self._pct(m["Net Income"], m["Total Assets"]),
                
                # === Leverage Ratios ===
                "Debt to Equity": self._ratio(m["Total Debt"], m["Total Equity"]),
                "Debt to Assets": self._ratio(m["Total Debt"], m["Total Assets"]),
                "Equity Ratio": self._ratio(m["Total Equity"], m["Total Assets"]),
                
                # === Liquidity Ratios ===
                "Current Ratio": self._ratio(m["Current Assets"], m["Current Liabilities"]),
                "Cash Ratio": self._ratio(m["Cash"], m["Current Liabilities"]),
                
                # === Efficiency / Cash Flow ===
                "Asset Turnover": self._ratio(m["Revenue"], m["Total Assets"]),
                "FCF Margin (%)": self._pct(m["Free Cash Flow"], m["Revenue"]),
                "OCF to Net Income": self._ratio(m["Operating Cash Flow"], m["Net Income"]),
            }
        
        df = pd.DataFrame(ratios)
        df = df[sorted(df.columns, reverse=True)]
        
        # Add growth rates
        df = self._add_growth_rates(df, metrics)
        
        return df
    
    def _pct(self, numerator: float, denominator: float) -> float:
        """Calculate percentage ratio safely."""
        if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
            return np.nan
        return round((numerator / denominator) * 100, 2)
    
    def _ratio(self, numerator: float, denominator: float) -> float:
        """Calculate ratio safely."""
        if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
            return np.nan
        return round(numerator / denominator, 2)
    
    def _add_growth_rates(self, ratios_df: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
        """Add year-over-year growth rates."""
        years = sorted(metrics.columns, reverse=True)
        
        growth_metrics = ["Revenue", "Net Income", "EPS", "Free Cash Flow"]
        
        for metric in growth_metrics:
            growth_row = {}
            for i, year in enumerate(years):
                if i < len(years) - 1:
                    current = metrics.loc[metric, year]
                    previous = metrics.loc[metric, years[i + 1]]
                    growth_row[year] = self._pct(current - previous, abs(previous)) if previous != 0 else np.nan
                else:
                    growth_row[year] = np.nan
            
            ratios_df.loc[f"{metric} Growth (%)"] = growth_row
        
        return ratios_df
    
    # =========================================================================
    # Export for LLM
    # =========================================================================
    
    def get_analysis_summary(self) -> Dict:
        """
        Generate a comprehensive summary for LLM analysis.
        
        Returns:
            Dictionary with all data structured for LLM consumption.
        """
        profile = self.get_company_profile()
        metrics = self.get_key_metrics()
        ratios = self.compute_ratios()
        
        # Convert to dict for JSON serialization
        def clean_for_json(df):
            return {
                str(col): {
                    str(idx): (None if pd.isna(val) else round(val, 2) if isinstance(val, float) else val)
                    for idx, val in df[col].items()
                }
                for col in df.columns
            }
        
        return {
            "company_profile": profile,
            "key_metrics": clean_for_json(metrics),
            "financial_ratios": clean_for_json(ratios),
            "data_periods": [str(c) for c in metrics.columns],
            "generated_at": datetime.now().isoformat(),
        }
    
    def export_for_llm(self, filepath: str) -> None:
        """Export analysis data to JSON file for LLM input."""
        data = self.get_analysis_summary()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported analysis to {filepath}")
    
    def export_to_csv(self, output_dir: str = ".") -> None:
        """Export all data to CSV files."""
        metrics = self.get_key_metrics()
        ratios = self.compute_ratios()
        
        metrics.to_csv(f"{output_dir}/{self.ticker}_metrics.csv")
        ratios.to_csv(f"{output_dir}/{self.ticker}_ratios.csv")
        
        logger.info(f"Exported CSVs to {output_dir}")
    
    def generate_llm_prompt_context(self) -> str:
        """
        Generate a text summary that can be directly used in an LLM prompt.
        
        Returns:
            Formatted string with all financial data.
        """
        profile = self.get_company_profile()
        metrics = self.get_key_metrics()
        ratios = self.compute_ratios()
        
        context = f"""
=== COMPANY PROFILE ===
Company: {profile['name']} ({self.ticker})
Sector: {profile['sector']}
Industry: {profile['industry']}
Market Cap: ${profile['market_cap']:,.0f}
Employees: {profile['employees']:,}

Description: {profile['description']}

=== KEY FINANCIAL METRICS (in millions USD) ===
{metrics.to_string()}

=== FINANCIAL RATIOS ===
{ratios.to_string()}
"""
        return context


# =============================================================================
# Quick Analysis Function
# =============================================================================

def analyze_company(ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Quick function to analyze any company.
    
    Args:
        ticker: Stock symbol or company name
        
    Returns:
        Tuple of (metrics_df, ratios_df, llm_context_string)
    """
    collector = FundamentalCollector(ticker)
    metrics = collector.get_key_metrics()
    ratios = collector.compute_ratios()
    context = collector.generate_llm_prompt_context()
    
    return metrics, ratios, context


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FUNDAMENTAL DATA COLLECTOR DEMO")
    print("=" * 70)
    
    # Initialize for Apple
    collector = FundamentalCollector("AAPL")
    
    # Get company profile
    print("\n[1] Company Profile:")
    print("-" * 40)
    profile = collector.get_company_profile()
    for key, value in profile.items():
        if key != "description":
            print(f"    {key}: {value}")
    
    # Get financial statements
    print("\n[2] Fetching Financial Statements...")
    print("-" * 40)
    statements = collector.get_all_statements()
    for name, df in statements.items():
        print(f"    {name}: {df.shape[0]} line items, {df.shape[1]} periods")
    
    # Get key metrics
    print("\n[3] Key Metrics (Last 5 Years):")
    print("-" * 40)
    metrics = collector.get_key_metrics()
    print(metrics.to_string())
    
    # Compute ratios
    print("\n[4] Financial Ratios:")
    print("-" * 40)
    ratios = collector.compute_ratios()
    print(ratios.to_string())
    
    # Generate LLM context
    print("\n[5] LLM Context Preview (first 500 chars):")
    print("-" * 40)
    context = collector.generate_llm_prompt_context()
    print(context[:500] + "...")
    
    print("\n" + "=" * 70)
    print("To switch companies, just change the ticker:")
    print('    collector = FundamentalCollector("MSFT")  # Microsoft')
    print('    collector = FundamentalCollector("BP.L")  # BP')
    print("=" * 70)
    
    # Save to CSV files
    collector.export_to_csv(".")
    
    # Also save raw statements
    statements["income_statement"].to_csv("AAPL_income_statement.csv")
    statements["balance_sheet"].to_csv("AAPL_balance_sheet.csv")
    statements["cash_flow"].to_csv("AAPL_cash_flow.csv")
    
    print("\n✓ CSV files saved!")