"""
Fundamental Data Collector
==========================
Collects financial statements from Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import json


class FundamentalCollector:
    """
    Collects financial statements for any company.
    
    Usage:
        collector = FundamentalCollector("AAPL")
        statements = collector.get_all_statements()
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
    
    # =========================================================================
    # Company Info
    # =========================================================================
    
    def get_company_profile(self) -> dict:
        """Get company information."""
        info = self.stock.info
        return {
            "ticker": self.ticker,
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "country": info.get("country", "N/A"),
            "currency": info.get("currency", "USD"),
            "market_cap": info.get("marketCap", 0),
            "employees": info.get("fullTimeEmployees", 0),
        }
    
    # =========================================================================
    # Financial Statements
    # =========================================================================
    
    def get_income_statement(self) -> pd.DataFrame:
        """Fetch annual income statement."""
        return self.stock.income_stmt
    
    def get_balance_sheet(self) -> pd.DataFrame:
        """Fetch annual balance sheet."""
        return self.stock.balance_sheet
    
    def get_cash_flow(self) -> pd.DataFrame:
        """Fetch annual cash flow statement."""
        return self.stock.cashflow
    
    def get_all_statements(self) -> dict:
        """Fetch all three financial statements."""
        return {
            "income_statement": self.get_income_statement(),
            "balance_sheet": self.get_balance_sheet(),
            "cash_flow": self.get_cash_flow(),
        }
    
    # =========================================================================
    # Export
    # =========================================================================
    
    def save_to_csv(self, output_dir: str = "."):
        """Save all statements to CSV files."""
        statements = self.get_all_statements()
        
        statements["income_statement"].to_csv(f"{output_dir}/{self.ticker}_income_statement.csv")
        statements["balance_sheet"].to_csv(f"{output_dir}/{self.ticker}_balance_sheet.csv")
        statements["cash_flow"].to_csv(f"{output_dir}/{self.ticker}_cash_flow.csv")
        
        print(f"Saved CSV files to {output_dir}")


if __name__ == "__main__":
    # Collect data for Apple
    collector = FundamentalCollector("DELL")
    
    # Get company info
    print("Company Profile:")
    print(collector.get_company_profile())
    
    # Get all statements
    print("\nFetching financial statements...")
    statements = collector.get_all_statements()
    
    for name, df in statements.items():
        print(f"  {name}: {df.shape[0]} rows, {df.shape[1]} years")
    
    # Save to CSV
    collector.save_to_csv("Dell_data")
    
    print("\nDone!")