# Fundamental Analyst Agent

An AI-powered investment analysis tool that simulates the role of a buy-side financial analyst within an asset management firm. The agent automates data collection, ratio analysis, forecasting, and report generation to produce institutional-grade investment memorandums.

Developed as part of MSc Banking and Financial Technology coursework (IFTE0001: Introduction to Financial Markets) at UCL.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Pipeline Architecture](#pipeline-architecture)
8. [Output Reports](#output-reports)
9. [Financial Metrics](#financial-metrics)
10. [Dependencies](#dependencies)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The Fundamental Analyst Agent performs comprehensive equity analysis by:

- Collecting 5 years of financial statement data (income statement, balance sheet, cash flow)
- Computing 35+ financial ratios across 7 categories
- Generating 4-year financial forecasts with Bull/Base/Bear scenarios
- Producing AI-generated investment analysis using GPT-4o-mini
- Exporting professional PDF reports with charts and visualizations

The system mirrors the analytical workflows of professional asset managers, integrating data engineering, quantitative finance, and artificial intelligence into an end-to-end solution.

---

## Features

- Automated data collection from Alpha Vantage API with local caching
- Real-time stock price and market data from Yahoo Finance
- Comprehensive ratio analysis (profitability, liquidity, leverage, efficiency, growth, risk, valuation)
- Multi-scenario financial forecasting (Bull, Base, Bear cases)
- Signal-based recommendation engine with confidence scoring
- AI-generated investment thesis, analysis sections, and risk assessment
- Professional 4-page PDF report with:
  - Executive summary with recommendation banner
  - Market profile and overall score metrics
  - Key financial metrics table with visual indicators
  - Signal analysis with thresholds
  - Charts (pie chart, bar chart, line chart, risk gauge)
  - 4-year forecast table and projections
  - Risk assessment and catalysts
  - Investment conclusion

---

## Project Structure

```
AI Codes/
|
|-- agent.py                 # Main entry point - run this file
|-- config.py                # API keys (Alpha Vantage, OpenAI)
|-- README.md                # This file
|-- requirements.txt         # Python dependencies
|
|-- src/                     # Source code modules
|   |-- __init__.py
|   |-- datacollector.py     # Fetches and caches financial statements
|   |-- forecast.py          # 4-year financial projections
|   |
|   |-- Ratios/              # Financial ratio calculation modules
|       |-- __init__.py
|       |-- profitability.py # Margins, ROE, ROA, ROCE, ROIC
|       |-- liquidity.py     # Current, Quick, Cash ratios
|       |-- leverage.py      # Debt/Equity, Interest Coverage, CF/Debt
|       |-- efficiency.py    # Asset Turnover, Receivables Turnover
|       |-- growth.py        # Revenue Growth, Net Income Growth
|       |-- risk.py          # Altman Z-Score, Risk Score
|       |-- valuation.py     # P/E, P/B, P/S, EV/EBITDA
|
|-- Reports/                 # Generated reports (auto-created)
|   |-- {TICKER}_report_{timestamp}.pdf
|   |-- {TICKER}_report_{timestamp}.json
|   |-- {TICKER}_report_{timestamp}.md
|
|-- {TICKER}_Data/           # Cached CSV files (auto-created)
|   |-- income_stmt.csv
|   |-- balance_sheet.csv
|   |-- cash_flow.csv
|
|-- venv/                    # Python virtual environment
```

---

## Installation

### 1. Clone or Download the Project

Place all files in your working directory (e.g., C:\Users\{username}\Desktop\AI Codes).

### 2. Create Virtual Environment

```powershell
cd "C:\Users\de3ah\OneDrive\Desktop\AI Codes"
python -m venv venv
```

### 3. Activate Virtual Environment

Windows PowerShell:
```powershell
.\venv\Scripts\Activate
```

Windows Command Prompt:
```cmd
venv\Scripts\activate.bat
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

Or install manually:
```powershell
pip install pandas numpy matplotlib yfinance openai reportlab requests
```

---

## Configuration

Create a config.py file in the project root with your API keys:

```python
# config.py

ALPHA_VANTAGE_KEY = "your_alpha_vantage_api_key"
OPENAI_KEY = "your_openai_api_key"
```

### Obtaining API Keys

Alpha Vantage (Free)
- Register at: https://www.alphavantage.co/support/#api-key
- Free tier: 25 requests/day

OpenAI
- Register at: https://platform.openai.com/api-keys
- Requires account with credits

---

## Usage

### Basic Usage

```powershell
python agent.py AAPL
```

### Force Data Refresh

```powershell
python agent.py AAPL --refresh
```

### Analyze Different Stocks

```powershell
python agent.py MSFT
python agent.py GOOGL
python agent.py TSLA
python agent.py BP.L
python agent.py SHEL.L
```

### Output

The agent displays progress through 6 steps and generates reports in the Reports/ directory.

Example output:
```
============================================================
  FUNDAMENTAL ANALYST AGENT
  Analyzing: AAPL
============================================================

============================================================
  STEP 1: DATA COLLECTION
============================================================
  [DataCollector] Loading AAPL from cache...
    Loaded 20 years from cache
  [MarketData] Fetching live price...
    Apple Inc.
    Price: $247.85 | MCap: $3,662.3B

============================================================
  STEP 2: RATIO ANALYSIS
============================================================
    Profitability...
    Liquidity...
    Leverage...
    Efficiency...
    Growth...
    Risk...
    Valuation...
    Calculated 36 ratios

============================================================
  STEP 3: FORECASTING
============================================================
    Generated 4-year projections

============================================================
  STEP 4: SCORING & RECOMMENDATION
============================================================
    Risk Score: 82/100 (LOW)
    Recommendation: BUY
    Confidence: 80%

============================================================
  STEP 5: AI REPORT GENERATION
============================================================
    Generating analysis sections...
    Generated 7 sections

============================================================
  AAPL: BUY | 80% | $309.81
============================================================

============================================================
  STEP 6: EXPORT
============================================================
    PDF:  Reports/AAPL_report_20260127_143052.pdf
    JSON: Reports/AAPL_report_20260127_143052.json
    MD:   Reports/AAPL_report_20260127_143052.md

  COMPLETE
```

---

## Pipeline Architecture

The agent executes a 6-step analytical pipeline:

### Step 1: Data Collection

```
Alpha Vantage API --> Income Statement
                  --> Balance Sheet
                  --> Cash Flow Statement

Yahoo Finance --> Current Price
              --> Market Cap
              --> Sector/Industry
```

- Fetches income statement, balance sheet, and cash flow data from Alpha Vantage
- Retrieves real-time price and market cap from Yahoo Finance
- Caches data locally in {TICKER}_Data/ folder to minimize API calls
- Supports 20 years of historical data

### Step 2: Ratio Analysis

Computes 35+ financial ratios across 7 categories:

| Category | Ratios |
|----------|--------|
| Profitability | Gross Margin, Operating Margin, Net Margin, EBITDA Margin, ROE, ROA, ROCE, ROIC |
| Liquidity | Current Ratio, Quick Ratio, Cash Ratio |
| Leverage | Debt/Equity, Debt/Assets, Interest Coverage, CF/Debt, Net Debt/EBITDA, Equity Multiplier |
| Efficiency | Asset Turnover, Receivables Turnover, Inventory Turnover, Payables Turnover |
| Growth | Revenue Growth, Net Income Growth, EPS Growth, Asset Growth |
| Risk | Altman Z-Score, Beneish M-Score, Financial Health Score |
| Valuation | P/E Ratio, P/B Ratio, P/S Ratio, EV/EBITDA, EV/Revenue |

### Step 3: Forecasting

Projects 4 years of financial data with three scenarios:

| Scenario | Description | Growth Assumption |
|----------|-------------|-------------------|
| Bull | Optimistic case | Historical growth + 2 std dev |
| Base | Expected case | Historical average growth |
| Bear | Pessimistic case | Historical growth - 2 std dev |

Forecasted metrics:
- Revenue
- Net Income
- Free Cash Flow
- Total Assets
- Total Debt

### Step 4: Scoring and Recommendation

Signal Generation:

| Metric | BUY Threshold | SELL Threshold |
|--------|---------------|----------------|
| Risk Score | > 70 | < 40 |
| Revenue Growth | > 10% | < 0% |
| Net Income Growth | > 10% | < 0% |
| ROE | > 15% | < 10% |
| Altman Z-Score | > 3.0 | < 1.81 |
| CF to Debt | > 0.5 | < 0.2 |
| Net Debt/EBITDA | < 2x | > 4x |
| Current Ratio | > 1.5 | < 1.0 |
| Net Margin | > 15% | < 5% |
| ROCE | > 15% | < 8% |

Recommendation Logic:
- BUY: Majority of signals are bullish
- SELL: Majority of signals are bearish
- HOLD: Mixed or neutral signals

Confidence = (Agreeing Signals / Total Signals) x 100

### Step 5: AI Report Generation

Sends financial data to GPT-4o-mini and generates structured analysis sections:

1. Investment Thesis - Why buy/hold/sell with target price
2. Profitability Analysis - Margin and return analysis
3. Leverage and Solvency - Debt and coverage analysis
4. Growth Outlook - Future projections and drivers
5. Key Risks - 4 specific risk factors
6. Potential Catalysts - 4 upside drivers
7. Investment Conclusion - Final verdict

### Step 6: Export

Generates three output files:

| Format | Purpose |
|--------|---------|
| PDF | Professional report with charts and tables |
| JSON | Structured data for programmatic access |
| Markdown | Text summary for documentation |

---

## Output Reports

### PDF Report Structure (4 Pages)

**Page 1: Executive Summary**
- Report header with date
- Company name, ticker, sector, industry
- Current price, market cap, target price display
- Recommendation banner (BUY/HOLD/SELL with color coding)
- Key metrics: Confidence, Return, Risk/Reward, Risk Rating
- Market profile table
- Overall score boxes (Financial Health, Profitability, Returns, Leverage, Liquidity, Growth, P/E)
- Investment thesis section
- Key financial metrics table with 28 ratios and visual indicators

**Page 2: Score Analysis**
- Signal breakdown table with buy/sell thresholds
- Signal distribution summary (Bullish/Neutral/Bearish counts)
- Signal distribution pie chart
- Profitability profile bar chart
- Profitability analysis narrative
- Leverage and solvency analysis narrative

**Page 3: Financial Forecast**
- 4-year projection table showing Bull/Base/Bear scenarios
- Metrics: Revenue, Net Income, Free Cash Flow, Total Debt
- Revenue projection line chart with confidence range
- Growth outlook narrative

**Page 4: Risk Assessment**
- Financial health score gauge (0-100 scale)
- Key risks section (4 bullet points)
- Potential catalysts section (4 bullet points)
- Investment conclusion narrative
- Final recommendation box
- Disclaimer

### JSON Report Structure

```json
{
  "ticker": "AAPL",
  "company": "Apple Inc.",
  "date": "January 27, 2026",
  "price": 247.85,
  "target": 309.81,
  "market_cap": 3662300000000,
  "recommendation": "BUY",
  "confidence": 80,
  "risk_score": 82,
  "risk_rating": "LOW",
  "ratios": {
    "profitability": {...},
    "liquidity": {...},
    "leverage": {...},
    "efficiency": {...},
    "growth": {...},
    "risk": {...},
    "valuation": {...}
  },
  "signals": {...},
  "forecast": {...},
  "analysis": {
    "THESIS": "...",
    "PROFITABILITY": "...",
    "LEVERAGE": "...",
    "GROWTH": "...",
    "RISKS": "...",
    "CATALYSTS": "...",
    "CONCLUSION": "..."
  }
}
```

---

## Financial Metrics

### Profitability Ratios

| Metric | Formula | Good | Bad |
|--------|---------|------|-----|
| Gross Margin | (Revenue - COGS) / Revenue | >40% | <20% |
| Operating Margin | Operating Income / Revenue | >20% | <10% |
| Net Margin | Net Income / Revenue | >15% | <5% |
| EBITDA Margin | EBITDA / Revenue | >25% | <10% |
| ROE | Net Income / Shareholders Equity | >15% | <10% |
| ROA | Net Income / Total Assets | >10% | <5% |
| ROCE | EBIT / Capital Employed | >15% | <8% |
| ROIC | NOPAT / Invested Capital | >12% | <8% |

### Leverage Ratios

| Metric | Formula | Good | Bad |
|--------|---------|------|-----|
| Debt/Equity | Total Debt / Shareholders Equity | <0.5x | >1.5x |
| Debt/Assets | Total Debt / Total Assets | <0.3 | >0.6 |
| Interest Coverage | EBIT / Interest Expense | >5x | <2x |
| CF to Debt | Operating Cash Flow / Total Debt | >0.5 | <0.2 |
| Net Debt/EBITDA | (Total Debt - Cash) / EBITDA | <2x | >4x |

### Liquidity Ratios

| Metric | Formula | Good | Bad |
|--------|---------|------|-----|
| Current Ratio | Current Assets / Current Liabilities | >1.5x | <1.0x |
| Quick Ratio | (Current Assets - Inventory) / Current Liabilities | >1.0x | <0.5x |
| Cash Ratio | Cash / Current Liabilities | >0.5x | <0.2x |

### Valuation Ratios

| Metric | Formula | Cheap | Expensive |
|--------|---------|-------|-----------|
| P/E Ratio | Price / Earnings Per Share | <15x | >30x |
| P/B Ratio | Price / Book Value Per Share | <3x | >10x |
| P/S Ratio | Market Cap / Revenue | <3x | >8x |
| EV/EBITDA | Enterprise Value / EBITDA | <10x | >20x |

### Risk Metrics

| Metric | Safe Zone | Gray Zone | Distress Zone |
|--------|-----------|-----------|---------------|
| Altman Z-Score | >2.99 | 1.81-2.99 | <1.81 |
| Risk Score | 70-100 (Low) | 40-70 (Moderate) | 0-40 (High) |

---

## Module Descriptions

### agent.py (Main Controller)

The central orchestrator that:
- Initializes all components
- Executes the 6-step pipeline
- Manages data flow between modules
- Generates the final PDF report
- Handles command-line arguments

### src/datacollector.py

Responsible for:
- Fetching financial statements from Alpha Vantage API
- Implementing rate limiting (5 calls/minute for free tier)
- Caching data locally in CSV format
- Loading cached data to minimize API usage

### src/forecast.py

Handles financial projections:
- Calculates historical growth rates
- Generates 4-year forecasts
- Produces Bull/Base/Bear scenarios
- Projects revenue, income, cash flow, assets, debt

### src/Ratios/profitability.py

Calculates profitability metrics:
- Gross Margin, Operating Margin, Net Margin
- EBITDA Margin
- ROE, ROA, ROCE, ROIC

### src/Ratios/liquidity.py

Calculates liquidity metrics:
- Current Ratio
- Quick Ratio
- Cash Ratio

### src/Ratios/leverage.py

Calculates leverage and solvency metrics:
- Debt/Equity, Debt/Assets
- Interest Coverage
- Cash Flow to Debt
- Net Debt/EBITDA
- Equity Multiplier

### src/Ratios/efficiency.py

Calculates efficiency metrics:
- Asset Turnover
- Receivables Turnover
- Inventory Turnover
- Payables Turnover

### src/Ratios/growth.py

Calculates growth metrics:
- Revenue Growth (YoY)
- Net Income Growth (YoY)
- EPS Growth
- Asset Growth

### src/Ratios/risk.py

Calculates risk metrics:
- Altman Z-Score (bankruptcy prediction)
- Beneish M-Score (earnings manipulation)
- Overall Financial Health Score

### src/Ratios/valuation.py

Calculates valuation multiples:
- P/E Ratio
- P/B Ratio
- P/S Ratio
- EV/EBITDA
- EV/Revenue

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=1.5.0 | Data manipulation and analysis |
| numpy | >=1.21.0 | Numerical computations |
| matplotlib | >=3.5.0 | Chart and graph generation |
| yfinance | >=0.2.0 | Real-time stock data from Yahoo Finance |
| openai | >=1.0.0 | GPT-4o-mini API for AI report generation |
| reportlab | >=4.0.0 | PDF document creation |
| requests | >=2.28.0 | HTTP requests for Alpha Vantage API |

### requirements.txt

```
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
yfinance>=0.2.0
openai>=1.0.0
reportlab>=4.0.0
requests>=2.28.0
```

---

## Troubleshooting

### "No module named 'src'"

Ensure you have an __init__.py file in the src folder:
```powershell
New-Item -Path "src\__init__.py" -ItemType File
```

### "No module named 'xyz'"

Install the missing package:
```powershell
pip install xyz
```

### "API rate limit exceeded" (Alpha Vantage)

The free tier allows 25 requests/day and 5 requests/minute. Solutions:
- Wait 60 seconds between runs
- Use cached data (do not use --refresh flag)
- Wait until the next day for daily limit reset
- Upgrade to premium API key

### "Invalid API key" (OpenAI)

- Verify your API key in config.py
- Check your OpenAI account has available credits
- Ensure the key has not expired
- Check for extra spaces or quotes in the key

### "Execution policy" error (PowerShell)

Run this command once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Charts not rendering in PDF

Ensure matplotlib is installed:
```powershell
pip install matplotlib
```

### "Style 'xyz' already defined" error

This occurs with older versions of agent.py. Download the latest version which uses unique style names.

### Empty or missing data in report

- Check that Alpha Vantage returned data (look for {TICKER}_Data/ folder)
- Some companies may not have all financial metrics available
- Try a different ticker to verify the system works

### OpenAI timeout or connection error

- Check your internet connection
- Verify OpenAI API status at status.openai.com
- Try running the script again

---

## Supported Tickers

The agent supports any ticker available on Alpha Vantage and Yahoo Finance:

**US Stocks:**
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Alphabet)
- AMZN (Amazon)
- TSLA (Tesla)
- META (Meta)
- NVDA (NVIDIA)

**UK Stocks (London Stock Exchange):**
- BP.L (BP)
- SHEL.L (Shell)
- ULVR.L (Unilever)
- RR.L (Rolls-Royce)

**European Stocks:**
- NESN.SW (Nestle - Swiss)
- SIE.DE (Siemens - German)

---

## License

This project is developed for educational purposes as part of the MSc Banking and Financial Technology program at UCL. It is not intended as investment advice.

---

## Author

MSc Banking and Financial Technology
UCL School of Management
IFTE0001: Introduction to Financial Markets
Track A: Fundamental Analyst Agent

---

## Disclaimer

This tool generates reports for educational purposes only. It does not constitute investment advice. Past performance does not guarantee future results. All investments involve risk of loss. Always conduct independent due diligence before making investment decisions.