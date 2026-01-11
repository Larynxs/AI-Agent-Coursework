"""
Data Collector (Alpha Vantage) - Fetches 5+ years of financial statements.
"""

import requests
import pandas as pd
from pathlib import Path


# Mapping: Alpha Vantage names -> Yahoo Finance names (what your ratio code expects)
NAME_MAP = {
    # Balance Sheet
    'totalAssets': 'Total Assets',
    'totalCurrentAssets': 'Current Assets',
    'totalCurrentLiabilities': 'Current Liabilities',
    'totalLiabilities': 'Total Liabilities Net Minority Interest',
    'totalShareholderEquity': 'Stockholders Equity',
    'retainedEarnings': 'Retained Earnings',
    'commonStock': 'Common Stock',
    'cashAndCashEquivalentsAtCarryingValue': 'Cash And Cash Equivalents',
    'inventory': 'Inventory',
    'currentNetReceivables': 'Accounts Receivable',
    'shortLongTermDebtTotal': 'Total Debt',
    'longTermDebt': 'Long Term Debt',
    'shortTermDebt': 'Current Debt',
    'propertyPlantEquipment': 'Net PPE',
    
    # Income Statement
    'totalRevenue': 'Total Revenue',
    'grossProfit': 'Gross Profit',
    'operatingIncome': 'Operating Income',
    'netIncome': 'Net Income',
    'ebit': 'EBIT',
    'ebitda': 'EBITDA',
    'interestExpense': 'Interest Expense',
    'interestIncome': 'Interest Income',
    'incomeTaxExpense': 'Tax Provision',
    'incomeBeforeTax': 'Pretax Income',
    'costOfRevenue': 'Cost Of Revenue',
    'operatingExpenses': 'Operating Expense',
    'researchAndDevelopment': 'Research And Development',
    'sellingGeneralAndAdministrative': 'Selling General And Administration',
    'depreciationAndAmortization': 'Reconciled Depreciation',
    
    # Cash Flow
    'operatingCashflow': 'Operating Cash Flow',
    'capitalExpenditures': 'Capital Expenditure',
    'cashflowFromInvestment': 'Investing Cash Flow',
    'cashflowFromFinancing': 'Financing Cash Flow',
    'dividendPayout': 'Cash Dividends Paid',
    'changeInCashAndCashEquivalents': 'Changes In Cash',
    'netIncome': 'Net Income From Continuing Operations',
}


class FundamentalCollector:
    """Collects financial statements from Alpha Vantage."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str, ticker: str):
        self.api_key = api_key
        self.ticker = ticker.upper()
    
    def _fetch(self, function: str) -> dict:
        """Fetch data from API."""
        params = {"function": function, "symbol": self.ticker, "apikey": self.api_key}
        data = requests.get(self.BASE_URL, params=params).json()
        if "Error Message" in data or "Note" in data:
            raise ValueError(data.get("Error Message") or data.get("Note"))
        return data
    
    def _to_dataframe(self, reports: list, years: int = 5) -> pd.DataFrame:
        """Convert API response to DataFrame with proper names."""
        df = pd.DataFrame(reports[:years]).set_index('fiscalDateEnding').T
        df = df.apply(pd.to_numeric, errors='coerce')
        df.index = df.index.map(lambda x: NAME_MAP.get(x, x))  # Rename rows
        return df
    
    def get_income_statement(self, years: int = 5) -> pd.DataFrame:
        return self._to_dataframe(self._fetch("INCOME_STATEMENT").get("annualReports", []), years)
    
    def get_balance_sheet(self, years: int = 5) -> pd.DataFrame:
        return self._to_dataframe(self._fetch("BALANCE_SHEET").get("annualReports", []), years)
    
    def get_cash_flow(self, years: int = 5) -> pd.DataFrame:
        return self._to_dataframe(self._fetch("CASH_FLOW").get("annualReports", []), years)
    
    def save_to_csv(self, output_dir: str = ".", years: int = 5):
        """Save all statements to CSV."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        statements = {
            "income_statement": self.get_income_statement(years),
            "balance_sheet": self.get_balance_sheet(years),
            "cash_flow": self.get_cash_flow(years),
        }
        
        for name, df in statements.items():
            df.to_csv(f"{output_dir}/{self.ticker}_{name}.csv")
        
        print(f"✅ Saved {years} years of data to {output_dir}/")


if __name__ == "__main__":
    API_KEY = "WZP8MYZRQ37CR5R3"
    TICKER = "AAPL"
    
    collector = FundamentalCollector(API_KEY, TICKER)
    collector.save_to_csv(f"APPL_Data", years=5)