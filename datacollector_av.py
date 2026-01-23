"""
Data Collector (Alpha Vantage) - Fetches 5+ years of financial statements.
"""

import requests
import pandas as pd
from pathlib import Path
import time


# Mapping: Alpha Vantage names -> Names your ratio code expects
INCOME_MAP = {
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
}

BALANCE_MAP = {
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
}

CASHFLOW_MAP = {
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
        response = requests.get(self.BASE_URL, params=params)
        data = response.json()
        
        # Check for various error conditions
        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        if "Note" in data:
            raise ValueError(f"API Rate Limit: {data['Note']}")
        if "Information" in data:
            raise ValueError(f"API Info: {data['Information']}")
        
        return data
    
    def _to_dataframe(self, reports: list, name_map: dict, years: int = 5) -> pd.DataFrame:
        """Convert API response to DataFrame with proper names."""
        if not reports:
            raise ValueError("No data returned from API. Check your API key and rate limits.")
        
        df = pd.DataFrame(reports[:years]).set_index('fiscalDateEnding').T
        df = df.apply(pd.to_numeric, errors='coerce')
        df.index = df.index.map(lambda x: name_map.get(x, x))
        return df
    
    def get_income_statement(self, years: int = 5) -> pd.DataFrame:
        data = self._fetch("INCOME_STATEMENT")
        reports = data.get("annualReports", [])
        return self._to_dataframe(reports, INCOME_MAP, years)
    
    def get_balance_sheet(self, years: int = 5) -> pd.DataFrame:
        data = self._fetch("BALANCE_SHEET")
        reports = data.get("annualReports", [])
        return self._to_dataframe(reports, BALANCE_MAP, years)
    
    def get_cash_flow(self, years: int = 5) -> pd.DataFrame:
        data = self._fetch("CASH_FLOW")
        reports = data.get("annualReports", [])
        return self._to_dataframe(reports, CASHFLOW_MAP, years)
    
    def save_to_csv(self, output_dir: str = ".", years: int = 5):
        """Save all statements to CSV."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Add delay between requests to avoid rate limiting
        print(f"Fetching income statement for {self.ticker}...")
        income = self.get_income_statement(years)
        time.sleep(12)  # Free tier: 5 calls/minute
        
        print(f"Fetching balance sheet for {self.ticker}...")
        balance = self.get_balance_sheet(years)
        time.sleep(12)
        
        print(f"Fetching cash flow for {self.ticker}...")
        cashflow = self.get_cash_flow(years)
        
        statements = {
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cashflow,
        }
        
        for name, df in statements.items():
            filepath = f"{output_dir}/{self.ticker}_{name}.csv"
            df.to_csv(filepath)
            print(f"  Saved: {filepath}")
        
        print(f"\nSaved {years} years of data to {output_dir}/")


if __name__ == "__main__":
    API_KEY = "05XJ6XAHDSFBNRS4"
    TICKER = "MSFT"
    
    collector = FundamentalCollector(API_KEY, TICKER)
    collector.save_to_csv("MSFT_Data", years=5)  # Fixed typo: APPL -> AAPL