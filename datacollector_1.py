"""
Data Collector - Fetches financial statements.
Sources: Yahoo Finance (free) or Alpha Vantage (25/day free)

API keys loaded from config.py (not committed to GitHub)
"""

import requests
import pandas as pd
import yfinance as yf
from pathlib import Path

# Try to import config
try:
    from config import ALPHA_VANTAGE_API_KEY
except ImportError:
    import os
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')


class DataCollector:
    """
    Collects financial statements from Yahoo Finance or Alpha Vantage.
    
    Usage:
        collector = DataCollector()                    # Yahoo (default)
        collector = DataCollector(source='alphavantage')  # Alpha Vantage
        
        data = collector.collect("AAPL")
        data = collector.collect_or_load("MSFT")       # Uses cache if exists
    """
    
    def __init__(self, source: str = 'yahoo', api_key: str = None):
        """
        Args:
            source: 'yahoo' (free) or 'alphavantage' (25/day)
            api_key: Alpha Vantage key (optional, loads from config.py)
        """
        self.source = source.lower()
        self.api_key = api_key or ALPHA_VANTAGE_API_KEY
        self.ticker = None
        
        if self.source == 'alphavantage':
            if not self.api_key or self.api_key == "YOUR_ALPHA_VANTAGE_KEY":
                raise ValueError("Add your Alpha Vantage API key to config.py")
    
    # ==================== YAHOO FINANCE ====================
    
    def _yahoo_income(self, ticker: str) -> pd.DataFrame:
        """Fetch income statement from Yahoo."""
        stock = yf.Ticker(ticker)
        df = stock.financials
        
        if df is None or df.empty:
            raise ValueError(f"No income data for {ticker}")
        
        # Rename columns to date strings
        df.columns = [str(c.date()) if hasattr(c, 'date') else str(c) for c in df.columns]
        
        # Standardize row names
        rename = {
            'Total Revenue': 'Total Revenue',
            'Gross Profit': 'Gross Profit',
            'Operating Income': 'Operating Income',
            'Net Income': 'Net Income',
            'EBITDA': 'EBITDA',
            'EBIT': 'EBIT',
            'Interest Expense': 'Interest Expense',
            'Tax Provision': 'Tax Provision',
            'Cost Of Revenue': 'Cost Of Revenue',
        }
        df.index = [rename.get(idx, idx) for idx in df.index]
        
        if 'EBIT' not in df.index and 'Operating Income' in df.index:
            df.loc['EBIT'] = df.loc['Operating Income']
        
        return df
    
    def _yahoo_balance(self, ticker: str) -> pd.DataFrame:
        """Fetch balance sheet from Yahoo."""
        stock = yf.Ticker(ticker)
        df = stock.balance_sheet
        
        if df is None or df.empty:
            raise ValueError(f"No balance sheet data for {ticker}")
        
        df.columns = [str(c.date()) if hasattr(c, 'date') else str(c) for c in df.columns]
        
        rename = {
            'Total Assets': 'Total Assets',
            'Current Assets': 'Current Assets',
            'Current Liabilities': 'Current Liabilities',
            'Total Liabilities Net Minority Interest': 'Total Liabilities Net Minority Interest',
            'Stockholders Equity': 'Stockholders Equity',
            'Common Stock Equity': 'Stockholders Equity',
            'Cash And Cash Equivalents': 'Cash And Cash Equivalents',
            'Cash Cash Equivalents And Short Term Investments': 'Cash And Cash Equivalents',
            'Inventory': 'Inventory',
            'Receivables': 'Accounts Receivable',
            'Accounts Receivable': 'Accounts Receivable',
            'Current Debt': 'Current Debt',
            'Long Term Debt': 'Long Term Debt',
            'Total Debt': 'Total Debt',
            'Net PPE': 'Net PPE',
            'Accounts Payable': 'Accounts Payable',
        }
        df.index = [rename.get(idx, idx) for idx in df.index]
        
        # Calculate Total Debt if missing
        if 'Total Debt' not in df.index:
            lt = df.loc['Long Term Debt'] if 'Long Term Debt' in df.index else 0
            st = df.loc['Current Debt'] if 'Current Debt' in df.index else 0
            df.loc['Total Debt'] = lt + st
        
        return df
    
    def _yahoo_cashflow(self, ticker: str) -> pd.DataFrame:
        """Fetch cash flow from Yahoo."""
        stock = yf.Ticker(ticker)
        df = stock.cashflow
        
        if df is None or df.empty:
            raise ValueError(f"No cash flow data for {ticker}")
        
        df.columns = [str(c.date()) if hasattr(c, 'date') else str(c) for c in df.columns]
        
        rename = {
            'Operating Cash Flow': 'Operating Cash Flow',
            'Capital Expenditure': 'Capital Expenditure',
            'Free Cash Flow': 'Free Cash Flow',
            'Financing Cash Flow': 'Financing Cash Flow',
            'Investing Cash Flow': 'Investing Cash Flow',
            'Cash Dividends Paid': 'Cash Dividends Paid',
            'Common Stock Dividend Paid': 'Cash Dividends Paid',
            'Depreciation And Amortization': 'Depreciation And Amortization',
        }
        df.index = [rename.get(idx, idx) for idx in df.index]
        
        return df
    
    # ==================== ALPHA VANTAGE ====================
    
    def _av_fetch(self, function: str, ticker: str) -> dict:
        """Fetch from Alpha Vantage API."""
        url = "https://www.alphavantage.co/query"
        params = {'function': function, 'symbol': ticker, 'apikey': self.api_key}
        
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        
        if "Error Message" in data:
            raise ValueError(f"Invalid ticker: {ticker}")
        if "Note" in data:
            raise ValueError("Alpha Vantage rate limit (25/day). Use 'yahoo' or wait.")
        if "Information" in data:
            raise ValueError(f"API error: {data['Information']}")
        
        return data
    
    def _av_parse(self, data: dict, key: str, rename: dict) -> pd.DataFrame:
        """Parse Alpha Vantage response to DataFrame."""
        if key not in data:
            raise ValueError(f"No {key} in response")
        
        reports = data[key]
        if not reports:
            raise ValueError(f"Empty {key}")
        
        records = {}
        for report in reports:
            date = report.get('fiscalDateEnding', 'Unknown')
            records[date] = {}
            for k, v in report.items():
                if k not in ['fiscalDateEnding', 'reportedCurrency']:
                    try:
                        records[date][k] = float(v) if v and v != 'None' else None
                    except:
                        records[date][k] = None
        
        df = pd.DataFrame(records)
        df.index = [rename.get(idx, idx) for idx in df.index]
        return df
    
    def _av_income(self, ticker: str) -> pd.DataFrame:
        """Fetch income statement from Alpha Vantage."""
        data = self._av_fetch('INCOME_STATEMENT', ticker)
        
        rename = {
            'totalRevenue': 'Total Revenue',
            'grossProfit': 'Gross Profit',
            'operatingIncome': 'Operating Income',
            'netIncome': 'Net Income',
            'ebitda': 'EBITDA',
            'ebit': 'EBIT',
            'interestExpense': 'Interest Expense',
            'incomeTaxExpense': 'Tax Provision',
            'costOfRevenue': 'Cost Of Revenue',
            'costofGoodsAndServicesSold': 'Cost Of Revenue',
        }
        
        df = self._av_parse(data, 'annualReports', rename)
        
        if 'EBIT' not in df.index and 'Operating Income' in df.index:
            df.loc['EBIT'] = df.loc['Operating Income']
        
        return df
    
    def _av_balance(self, ticker: str) -> pd.DataFrame:
        """Fetch balance sheet from Alpha Vantage."""
        data = self._av_fetch('BALANCE_SHEET', ticker)
        
        rename = {
            'totalAssets': 'Total Assets',
            'totalCurrentAssets': 'Current Assets',
            'totalCurrentLiabilities': 'Current Liabilities',
            'totalLiabilities': 'Total Liabilities Net Minority Interest',
            'totalShareholderEquity': 'Stockholders Equity',
            'cashAndCashEquivalentsAtCarryingValue': 'Cash And Cash Equivalents',
            'cashAndShortTermInvestments': 'Cash And Cash Equivalents',
            'inventory': 'Inventory',
            'currentNetReceivables': 'Accounts Receivable',
            'shortTermDebt': 'Current Debt',
            'longTermDebt': 'Long Term Debt',
            'shortLongTermDebtTotal': 'Total Debt',
            'propertyPlantEquipment': 'Net PPE',
        }
        
        df = self._av_parse(data, 'annualReports', rename)
        
        if 'Total Debt' not in df.index:
            lt = df.loc['Long Term Debt'] if 'Long Term Debt' in df.index else 0
            st = df.loc['Current Debt'] if 'Current Debt' in df.index else 0
            df.loc['Total Debt'] = lt + st
        
        return df
    
    def _av_cashflow(self, ticker: str) -> pd.DataFrame:
        """Fetch cash flow from Alpha Vantage."""
        data = self._av_fetch('CASH_FLOW', ticker)
        
        rename = {
            'operatingCashflow': 'Operating Cash Flow',
            'capitalExpenditures': 'Capital Expenditure',
            'cashflowFromInvestment': 'Investing Cash Flow',
            'cashflowFromFinancing': 'Financing Cash Flow',
            'dividendPayout': 'Cash Dividends Paid',
            'depreciationDepletionAndAmortization': 'Depreciation And Amortization',
        }
        
        return self._av_parse(data, 'annualReports', rename)
    
    # ==================== MAIN METHODS ====================
    
    def collect(self, ticker: str, output_dir: str = None) -> dict:
        """
        Collect all financial statements for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            output_dir: Where to save CSVs (default: {TICKER}_Data/)
        
        Returns:
            dict with income_stmt, balance_sheet, cash_flow DataFrames
        """
        self.ticker = ticker.upper()
        
        if output_dir is None:
            output_dir = f"{self.ticker}_Data"
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"\n  Collecting {self.ticker} via {self.source}...")
        
        if self.source == 'yahoo':
            print(f"    [1/3] Income Statement...")
            income = self._yahoo_income(self.ticker)
            print(f"    [2/3] Balance Sheet...")
            balance = self._yahoo_balance(self.ticker)
            print(f"    [3/3] Cash Flow...")
            cashflow = self._yahoo_cashflow(self.ticker)
        else:  # alphavantage
            print(f"    [1/3] Income Statement...")
            income = self._av_income(self.ticker)
            print(f"    [2/3] Balance Sheet...")
            balance = self._av_balance(self.ticker)
            print(f"    [3/3] Cash Flow...")
            cashflow = self._av_cashflow(self.ticker)
        
        # Save CSVs
        income.to_csv(f"{output_dir}/{self.ticker}_income_statement.csv")
        balance.to_csv(f"{output_dir}/{self.ticker}_balance_sheet.csv")
        cashflow.to_csv(f"{output_dir}/{self.ticker}_cash_flow.csv")
        
        print(f"    ✓ Saved {len(income.columns)} years to {output_dir}/")
        
        return {
            'income_stmt': income,
            'balance_sheet': balance,
            'cash_flow': cashflow,
            'output_dir': output_dir
        }
    
    def load_existing(self, ticker: str, data_dir: str = None) -> dict:
        """Load from cached CSV files."""
        self.ticker = ticker.upper()
        
        if data_dir is None:
            data_dir = f"{self.ticker}_Data"
        
        paths = [
            Path(data_dir) / f"{self.ticker}_income_statement.csv",
            Path(data_dir) / f"{self.ticker}_balance_sheet.csv",
            Path(data_dir) / f"{self.ticker}_cash_flow.csv"
        ]
        
        if not all(p.exists() for p in paths):
            return None
        
        print(f"\n  Loading cached data for {self.ticker}...")
        
        return {
            'income_stmt': pd.read_csv(paths[0], index_col=0),
            'balance_sheet': pd.read_csv(paths[1], index_col=0),
            'cash_flow': pd.read_csv(paths[2], index_col=0),
            'output_dir': data_dir
        }
    
    def collect_or_load(self, ticker: str, force_refresh: bool = False) -> dict:
        """Load from cache or fetch new data."""
        self.ticker = ticker.upper()
        
        if not force_refresh:
            cached = self.load_existing(self.ticker)
            if cached:
                print(f"    ✓ Using cached data")
                return cached
        
        return self.collect(self.ticker)


# ==================== CLI TEST ====================

if __name__ == "__main__":
    import sys
    
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    source = sys.argv[2] if len(sys.argv) > 2 else "yahoo"
    
    print(f"\n{'='*50}")
    print(f"  DATA COLLECTOR TEST")
    print(f"  Ticker: {ticker} | Source: {source}")
    print(f"{'='*50}")
    
    try:
        collector = DataCollector(source=source)
        data = collector.collect(ticker)
        
        print(f"\n  Results:")
        print(f"    Income Statement: {data['income_stmt'].shape}")
        print(f"    Balance Sheet:    {data['balance_sheet'].shape}")
        print(f"    Cash Flow:        {data['cash_flow'].shape}")
        
        inc = data['income_stmt']
        bal = data['balance_sheet']
        
        print(f"\n  Sample ({ticker}):")
        if 'Total Revenue' in inc.index:
            rev = inc.loc['Total Revenue'].iloc[0]
            print(f"    Revenue:      ${rev/1e9:.1f}B" if pd.notna(rev) else "    Revenue: N/A")
        if 'Net Income' in inc.index:
            ni = inc.loc['Net Income'].iloc[0]
            print(f"    Net Income:   ${ni/1e9:.1f}B" if pd.notna(ni) else "    Net Income: N/A")
        if 'Total Assets' in bal.index:
            ta = bal.loc['Total Assets'].iloc[0]
            print(f"    Total Assets: ${ta/1e9:.1f}B" if pd.notna(ta) else "    Total Assets: N/A")
        
        print(f"\n  ✓ Success!")
        
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
