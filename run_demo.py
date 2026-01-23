"""
Run Demo - Full Risk & Leverage Analysis Pipeline
MSc Coursework: AI Analyst Agents in Asset Management

This script demonstrates the complete workflow:
1. Collect financial data (5 years)
2. Calculate all ratios
3. Generate AI-powered risk assessment report
"""

import os
import sys

# Check dependencies
def check_dependencies():
    """Check if required packages are installed."""
    required = ['pandas', 'numpy', 'yfinance', 'openai', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        sys.exit(1)
    
    print("✅ All dependencies installed")


def main():
    """Run the full demo pipeline."""
    
    print("\n" + "=" * 70)
    print("  RISK & LEVERAGE ANALYSIS AGENT - DEMO")
    print("  MSc Coursework: AI Analyst Agents in Asset Management")
    print("=" * 70)
    
    # Step 0: Check dependencies
    print("\n[0/3] Checking dependencies...")
    check_dependencies()
    
    # Get user input
    print("\n" + "-" * 70)
    ticker = input("  Enter stock ticker (default: AAPL): ").strip().upper() or "AAPL"
    print("-" * 70)
    
    data_dir = f"{ticker}_Data"
    
    # Step 1: Collect data
    print(f"\n[1/3] Collecting financial data for {ticker}...")
    
    if os.path.exists(data_dir):
        use_existing = input(f"  Data folder '{data_dir}' exists. Use existing? (y/n): ").strip().lower()
        if use_existing != 'y':
            collect_data = True
        else:
            collect_data = False
            print(f"  Using existing data in {data_dir}/")
    else:
        collect_data = True
    
    if collect_data:
        from datacollector_av import FundamentalCollector
        
        API_KEY = "WZP8MYZRQ37CR5R3"  # Alpha Vantage API key
        
        try:
            collector = FundamentalCollector(API_KEY, ticker)
            collector.save_to_csv(data_dir, years=5)
        except Exception as e:
            print(f"  ❌ Error collecting data: {e}")
            print("  Note: Alpha Vantage has rate limits (25 requests/day)")
            sys.exit(1)
    
    # Step 2: Run ratio analysis
    print(f"\n[2/3] Running fundamental analysis...")
    
    from fundamental_analysis import FundamentalAnalysis
    import yfinance as yf
    
    # Get market cap
    stock = yf.Ticker(ticker)
    market_cap = stock.info.get('marketCap', 0)
    
    analysis = FundamentalAnalysis(
        ticker=ticker,
        data_dir=data_dir,
        market_cap=market_cap
    )
    analysis.run_all()
    
    # Step 3: Generate AI report
    print(f"\n[3/3] Generating AI risk assessment...")
    
    from memo_generator import RiskAnalysisAgent
    
    agent = RiskAnalysisAgent(
        ticker=ticker,
        data_dir=data_dir
    )
    agent.get_ratios()
    agent.calculate_risk_score()
    agent.print_quantitative_summary()
    
    print("\n" + "-" * 70)
    generate_ai = input("  Generate AI report? (y/n): ").strip().lower()
    print("-" * 70)
    
    if generate_ai == 'y':
        report = agent.generate_report()
        
        # Save report
        output_file = f"{ticker}_risk_report.md"
        with open(output_file, 'w') as f:
            f.write(f"# {agent.company_name} ({ticker}) - Risk Assessment\n\n")
            f.write(f"**Stock Price:** ${agent.current_price:,.2f}  \n")
            f.write(f"**Market Cap:** ${agent.market_cap/1e9:,.1f}B  \n")
            f.write(f"**Risk Score:** {agent.risk_score}/100  \n")
            f.write(f"**Risk Rating:** {agent.risk_rating}  \n")
            f.write(f"**Recommendation:** {agent.recommendation}  \n\n")
            f.write("---\n\n")
            f.write(report)
        
        print("\n" + "=" * 70)
        print("  AI RISK REPORT")
        print("=" * 70)
        print(report)
        print(f"\n✅ Report saved: {output_file}")
    
    # Done
    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)
    print(f"\n  Files generated:")
    print(f"  - {data_dir}/ (financial statements)")
    if generate_ai == 'y':
        print(f"  - {output_file} (AI risk report)")
    print()


if __name__ == "__main__":
    main()