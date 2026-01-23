"""
Fundamental Analyst Agent
AI-powered investment analysis with institutional-grade PDF reports.

Usage:
    python agent.py AAPL
    python agent.py MSFT --refresh
"""

import sys
import json
import io
import openai
import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# PDF imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

# Charts
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import components
from config import ALPHA_VANTAGE_KEY, OPENAI_KEY
from datacollector import DataCollector
from Ratios.profitability import ProfitabilityAnalysis
from Ratios.liquidity import LiquidityAnalysis
from Ratios.leverage import LeverageAnalysis
from Ratios.efficiency import EfficiencyAnalysis
from Ratios.growth import GrowthAnalysis
from Ratios.risk import RiskAnalysis
from Ratios.valuation import ValuationAnalysis
from forecast import FinancialForecast


class FundamentalAgent:
    """AI Agent for complete fundamental analysis."""
    
    def __init__(self):
        self.collector = DataCollector(api_key=ALPHA_VANTAGE_KEY)
        openai.api_key = OPENAI_KEY
        
        self.ticker = None
        self.company_name = None
        self.sector = None
        self.current_price = 0
        self.market_cap = 0
        
        self.income_stmt = None
        self.balance_sheet = None
        self.cash_flow = None
        
        self.ratios = {}
        self.forecast = {}
        self.forecast_years = []
        self.risk_score = 0
        self.risk_rating = ""
        self.recommendation = ""
        self.confidence = 0
        self.confidence_label = ""
        self.target_price = 0
        self.signal_breakdown = {}
        self.report_sections = {}
        
        self.timestamp = None
        self.report_date = None
    
    def _fmt(self, value, decimals=2):
        if pd.isna(value) or value is None:
            return "N/A"
        return f"{value:.{decimals}f}"
    
    # ==================== STEP 1: DATA ====================
    
    def _collect_data(self, ticker: str, refresh: bool = False):
        print(f"\n{'='*60}")
        print(f"  STEP 1: DATA COLLECTION")
        print(f"{'='*60}")
        
        data = self.collector.get(ticker, refresh=refresh)
        
        self.income_stmt = data['income_stmt']
        self.balance_sheet = data['balance_sheet']
        self.cash_flow = data['cash_flow']
        
        print(f"\n  [MarketData] Fetching live price...")
        stock = yf.Ticker(ticker)
        info = stock.info
        
        self.company_name = info.get('longName', ticker)
        self.sector = info.get('sector', 'Unknown')
        self.industry = info.get('industry', 'Unknown')
        self.current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        self.market_cap = info.get('marketCap', 0)
        
        print(f"    ✓ {self.company_name}")
        print(f"    ✓ Price: ${self.current_price:,.2f} | MCap: ${self.market_cap/1e9:,.1f}B")
    
    # ==================== STEP 2: RATIOS ====================
    
    def _calculate_ratios(self):
        print(f"\n{'='*60}")
        print(f"  STEP 2: RATIO ANALYSIS")
        print(f"{'='*60}")
        
        print(f"    → Profitability...")
        prof = ProfitabilityAnalysis(self.income_stmt, self.balance_sheet)
        prof.calculate_all()
        self.ratios['profitability'] = prof.get_latest_values()
        
        print(f"    → Liquidity...")
        liq = LiquidityAnalysis(self.balance_sheet)
        liq.calculate_all()
        self.ratios['liquidity'] = liq.get_latest_values()
        
        print(f"    → Leverage...")
        lev = LeverageAnalysis(self.income_stmt, self.balance_sheet, self.cash_flow)
        lev.calculate_all()
        self.ratios['leverage'] = lev.get_latest_values()
        
        print(f"    → Efficiency...")
        eff = EfficiencyAnalysis(self.income_stmt, self.balance_sheet)
        eff.calculate_all()
        self.ratios['efficiency'] = eff.get_latest_values()
        
        print(f"    → Growth...")
        grow = GrowthAnalysis(self.income_stmt)
        grow.calculate_all()
        self.ratios['growth'] = grow.get_latest_values()
        
        print(f"    → Risk...")
        risk = RiskAnalysis(self.income_stmt, self.balance_sheet, self.market_cap)
        risk.calculate_all()
        self.ratios['risk'] = risk.get_latest_values()
        
        print(f"    → Valuation...")
        try:
            val = ValuationAnalysis(self.ticker, self.income_stmt, self.balance_sheet)
            val.calculate_all()
            self.ratios['valuation'] = val.get_latest_values()
        except:
            self.ratios['valuation'] = {}
        
        total = sum(len(v) for v in self.ratios.values())
        print(f"    ✓ Calculated {total} ratios")
    
    # ==================== STEP 3: FORECAST ====================
    
    def _run_forecast(self):
        print(f"\n{'='*60}")
        print(f"  STEP 3: FORECASTING")
        print(f"{'='*60}")
        
        try:
            forecaster = FinancialForecast(self.income_stmt, self.balance_sheet, self.cash_flow)
            self.forecast = forecaster.calculate_all()
            self.forecast_years = forecaster.get_forecast_years()
            print(f"    ✓ Generated 4-year projections")
        except Exception as e:
            print(f"    ⚠ Forecast skipped: {e}")
            self.forecast = {}
            self.forecast_years = ['Y1', 'Y2', 'Y3', 'Y4']
    
    # ==================== STEP 4: SCORE ====================
    
    def _calculate_score(self):
        print(f"\n{'='*60}")
        print(f"  STEP 4: SCORING & RECOMMENDATION")
        print(f"{'='*60}")
        
        score = 0
        z = self.ratios['risk'].get('altman_z_score', 0)
        if pd.notna(z):
            score += 30 if z > 3.0 else 25 if z > 2.5 else 15 if z > 1.81 else 5
        
        cfd = self.ratios['leverage'].get('cash_flow_to_debt', 0)
        if pd.notna(cfd):
            score += 20 if cfd > 0.5 else 15 if cfd > 0.3 else 10 if cfd > 0.2 else 5
        
        nm = self.ratios['profitability'].get('net_margin', 0)
        if pd.notna(nm):
            score += 20 if nm > 20 else 16 if nm > 15 else 12 if nm > 10 else 8 if nm > 5 else 4
        
        de = self.ratios['leverage'].get('debt_to_equity', 999)
        if pd.notna(de):
            score += 15 if de < 0.5 else 12 if de < 1.0 else 9 if de < 1.5 else 6 if de < 2.0 else 3
        
        cr = self.ratios['liquidity'].get('current_ratio', 0)
        if pd.notna(cr):
            score += 15 if cr > 2.0 else 12 if cr > 1.5 else 9 if cr > 1.0 else 6 if cr > 0.8 else 3
        
        self.risk_score = score
        self.risk_rating = "VERY LOW" if score >= 85 else "LOW" if score >= 70 else "MODERATE" if score >= 55 else "ELEVATED" if score >= 40 else "HIGH"
        
        # Signals
        checks = [
            ('Risk Score', self.risk_score, 70, 40, False),
            ('Revenue Growth', self.ratios['growth'].get('revenue_growth', 0), 10, 0, False),
            ('Net Income Growth', self.ratios['growth'].get('net_income_growth', 0), 10, 0, False),
            ('ROE', self.ratios['profitability'].get('roe', 0), 15, 10, False),
            ('Altman Z-Score', self.ratios['risk'].get('altman_z_score', 0), 3.0, 1.81, False),
            ('CF to Debt', self.ratios['leverage'].get('cash_flow_to_debt', 0), 0.5, 0.2, False),
            ('Net Debt/EBITDA', self.ratios['leverage'].get('net_debt_to_ebitda', 5), 2, 4, True),
            ('Current Ratio', self.ratios['liquidity'].get('current_ratio', 0), 1.5, 1.0, False),
            ('Net Margin', self.ratios['profitability'].get('net_margin', 0), 15, 5, False),
            ('ROCE', self.ratios['profitability'].get('roce', 0), 15, 8, False)
        ]
        
        buy, sell = 0, 0
        for name, val, buy_th, sell_th, inverted in checks:
            val = 0 if pd.isna(val) else val
            if inverted:
                sig = 'BUY' if val < buy_th else 'SELL' if val > sell_th else 'HOLD'
            else:
                sig = 'BUY' if val > buy_th else 'SELL' if val < sell_th else 'HOLD'
            self.signal_breakdown[name] = (sig, f"{val:.2f}")
            buy += 1 if sig == 'BUY' else 0
            sell += 1 if sig == 'SELL' else 0
        
        self.buy_signals, self.sell_signals = buy, sell
        self.hold_signals = len(checks) - buy - sell
        
        if buy > sell and buy >= self.hold_signals:
            self.recommendation, agreeing = "BUY", buy
        elif sell > buy and sell >= self.hold_signals:
            self.recommendation, agreeing = "SELL", sell
        else:
            self.recommendation, agreeing = "HOLD", self.hold_signals
        
        self.confidence = (agreeing / len(checks)) * 100
        self.confidence_label = "VERY HIGH" if self.confidence >= 80 else "HIGH" if self.confidence >= 60 else "MODERATE" if self.confidence >= 40 else "LOW"
        
        self.target_price = self.current_price * (1.25 if self.recommendation == "BUY" else 0.85 if self.recommendation == "SELL" else 1.05)
        self.upside = ((self.target_price / self.current_price) - 1) * 100
        
        print(f"    → Risk Score: {self.risk_score}/100 ({self.risk_rating})")
        print(f"    → Recommendation: {self.recommendation}")
        print(f"    → Confidence: {self.confidence:.0f}%")
    
    # ==================== STEP 5: AI REPORT ====================
    
    def _generate_ai_report(self):
        print(f"\n{'='*60}")
        print(f"  STEP 5: AI REPORT GENERATION")
        print(f"{'='*60}")
        
        # Build forecast summary
        fc_text = ""
        if self.forecast and 'revenue' in self.forecast:
            fc_text = f"""
FORECAST (4-Year):
- Revenue Y4: Base ${self.forecast['revenue']['base'][-1]/1e9:.1f}B, Bull ${self.forecast['revenue']['bull'][-1]/1e9:.1f}B, Bear ${self.forecast['revenue']['bear'][-1]/1e9:.1f}B
- Net Income Y4: Base ${self.forecast.get('net_income', {}).get('base', [0])[-1]/1e9:.1f}B
- FCF Y4: Base ${self.forecast.get('free_cash_flow', {}).get('base', [0])[-1]/1e9:.1f}B"""

        prompt = f"""You are a senior equity analyst at Goldman Sachs Asset Management. Write professional analysis sections for {self.company_name} ({self.ticker}).

COMPANY: {self.company_name} | {self.sector} | {self.industry}
PRICE: ${self.current_price:,.2f} | MCAP: ${self.market_cap/1e9:,.1f}B | TARGET: ${self.target_price:,.2f} ({self.upside:+.1f}%)

RECOMMENDATION: {self.recommendation} | CONFIDENCE: {self.confidence:.0f}% | RISK: {self.risk_rating}

METRICS:
- Profitability: GM={self._fmt(self.ratios['profitability'].get('gross_margin'))}%, OM={self._fmt(self.ratios['profitability'].get('operating_margin'))}%, NM={self._fmt(self.ratios['profitability'].get('net_margin'))}%
- Returns: ROE={self._fmt(self.ratios['profitability'].get('roe'))}%, ROA={self._fmt(self.ratios['profitability'].get('roa'))}%, ROCE={self._fmt(self.ratios['profitability'].get('roce'))}%
- Leverage: D/E={self._fmt(self.ratios['leverage'].get('debt_to_equity'))}x, IntCov={self._fmt(self.ratios['leverage'].get('interest_coverage'))}x, CF/Debt={self._fmt(self.ratios['leverage'].get('cash_flow_to_debt'))}
- Liquidity: CR={self._fmt(self.ratios['liquidity'].get('current_ratio'))}x, QR={self._fmt(self.ratios['liquidity'].get('quick_ratio'))}x
- Growth: Rev={self._fmt(self.ratios['growth'].get('revenue_growth'))}%, NI={self._fmt(self.ratios['growth'].get('net_income_growth'))}%
- Risk: Z-Score={self._fmt(self.ratios['risk'].get('altman_z_score'))}, Score={self.risk_score}/100
{fc_text}

SIGNALS: {self.buy_signals} BUY, {self.hold_signals} HOLD, {self.sell_signals} SELL

Write these EXACT sections (use ||| as separator between sections):

|||THESIS|||
2 dense paragraphs: Why {self.recommendation}? State target ${self.target_price:,.2f} and {self.upside:+.1f}% upside. Reference specific metrics. Be assertive.

|||PROFITABILITY|||
2 paragraphs analyzing margins and returns. Use ALL the numbers provided. Compare to benchmarks.

|||LEVERAGE|||
2 paragraphs on debt, coverage, solvency. Discuss Z-Score={self._fmt(self.ratios['risk'].get('altman_z_score'))} implications.

|||GROWTH|||
2 paragraphs on growth trajectory and forecast. Use forecast numbers if available.

|||RISKS|||
4 bullet points (use - prefix). Specific, quantified risks.

|||CATALYSTS|||
4 bullet points (use - prefix). Specific drivers of upside.

|||CONCLUSION|||
1 paragraph final verdict with target price and confidence level.

Be specific with ALL numbers. Professional institutional tone. No generic statements."""

        print(f"    → Generating analysis sections...")
        
        client = openai.OpenAI(api_key=OPENAI_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0.7
        )
        
        raw = response.choices[0].message.content
        
        # Parse sections
        self.report_sections = {}
        for section in ['THESIS', 'PROFITABILITY', 'LEVERAGE', 'GROWTH', 'RISKS', 'CATALYSTS', 'CONCLUSION']:
            tag = f"|||{section}|||"
            if tag in raw:
                start = raw.find(tag) + len(tag)
                end = raw.find("|||", start) if "|||" in raw[start:] else len(raw)
                self.report_sections[section] = raw[start:end].strip()
        
        print(f"    ✓ Generated {len(self.report_sections)} sections")
    
    # ==================== STEP 6: EXPORT ====================
    
    def _export(self):
        print(f"\n{'='*60}")
        print(f"  STEP 6: EXPORT")
        print(f"{'='*60}")
        
        reports_dir = Path("Reports")
        reports_dir.mkdir(exist_ok=True)
        
        base = f"{self.ticker}_report_{self.timestamp}"
        
        pdf = self._save_pdf(reports_dir / f"{base}.pdf")
        js = self._save_json(reports_dir / f"{base}.json")
        md = self._save_md(reports_dir / f"{base}.md")
        
        print(f"    ✓ PDF:  {pdf}")
        print(f"    ✓ JSON: {js}")
        print(f"    ✓ MD:   {md}")
        
        return {'pdf': pdf, 'json': js, 'md': md}
    
    def _save_json(self, path):
        data = {
            "ticker": self.ticker, "company": self.company_name, "date": self.report_date,
            "price": self.current_price, "target": self.target_price, "market_cap": self.market_cap,
            "recommendation": self.recommendation, "confidence": self.confidence,
            "risk_score": self.risk_score, "risk_rating": self.risk_rating,
            "ratios": {k: {kk: float(vv) if pd.notna(vv) else None for kk, vv in v.items()} for k, v in self.ratios.items()},
            "signals": {k: {"signal": v[0], "value": v[1]} for k, v in self.signal_breakdown.items()},
            "forecast": self.forecast,
            "analysis": self.report_sections
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return path
    
    def _save_md(self, path):
        md = f"# {self.ticker} Investment Report\n\n**{self.recommendation}** | Target: ${self.target_price:,.2f} | Confidence: {self.confidence:.0f}%\n\n"
        for section, content in self.report_sections.items():
            md += f"## {section}\n\n{content}\n\n"
        with open(path, 'w') as f:
            f.write(md)
        return path
    
    # ==================== PDF REPORT ====================
    
    def _save_pdf(self, path):
        """Generate institutional-grade PDF report."""
        
        doc = SimpleDocTemplate(str(path), pagesize=letter, 
                               topMargin=0.3*inch, bottomMargin=0.3*inch, 
                               leftMargin=0.4*inch, rightMargin=0.4*inch)
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        DARK_BLUE = colors.HexColor('#1a365d')
        BLUE = colors.HexColor('#2c5282')
        GREEN = colors.HexColor('#276749')
        RED = colors.HexColor('#c53030')
        YELLOW = colors.HexColor('#b7791f')
        GRAY = colors.HexColor('#4a5568')
        LIGHT = colors.HexColor('#f7fafc')
        
        styles.add(ParagraphStyle('Title1', fontSize=20, textColor=DARK_BLUE, fontName='Helvetica-Bold', spaceAfter=2))
        styles.add(ParagraphStyle('Title2', fontSize=14, textColor=DARK_BLUE, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6))
        styles.add(ParagraphStyle('Title3', fontSize=11, textColor=BLUE, fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4))
        styles.add(ParagraphStyle('Body', fontSize=9, textColor=GRAY, leading=12, spaceAfter=6))
        styles.add(ParagraphStyle('Bullet', fontSize=9, textColor=GRAY, leading=11, leftIndent=15, spaceAfter=3))
        styles.add(ParagraphStyle('Small', fontSize=7, textColor=colors.HexColor('#718096')))
        styles.add(ParagraphStyle('Footer', fontSize=7, textColor=colors.HexColor('#a0aec0'), alignment=1))
        
        story = []
        rec_color = GREEN if self.recommendation == 'BUY' else RED if self.recommendation == 'SELL' else YELLOW
        
        # ==================== PAGE 1 ====================
        
        # Header
        hdr = Table([['FUNDAMENTAL ANALYST REPORT', f'{self.report_date}']], colWidths=[5.5*inch, 2*inch])
        hdr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), DARK_BLUE),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (0,0), 8),
            ('RIGHTPADDING', (1,0), (1,0), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(hdr)
        story.append(Spacer(1, 0.15*inch))
        
        # Title block
        story.append(Paragraph(self.ticker, styles['Title1']))
        story.append(Paragraph(f"<font color='#4a5568'>{self.company_name}</font>", styles['Normal']))
        story.append(Paragraph(f"<font size=8 color='#718096'>{self.sector} | {self.industry}</font>", styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Main recommendation banner
        rec_data = [
            [self.recommendation],
            ['CONFIDENCE', 'TARGET', 'RETURN', 'RISK'],
            [f"{self.confidence:.0f}%", f"${self.target_price:,.2f}", f"{self.upside:+.1f}%", self.risk_rating]
        ]
        rec_tbl = Table(rec_data, colWidths=[7.5*inch/4]*4)
        rec_tbl.setStyle(TableStyle([
            ('SPAN', (0,0), (-1,0)),
            ('BACKGROUND', (0,0), (-1,0), rec_color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 32),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0,1), (-1,1), 7),
            ('FONTNAME', (0,2), (-1,2), 'Helvetica-Bold'),
            ('FONTSIZE', (0,2), (-1,2), 12),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, DARK_BLUE),
        ]))
        story.append(rec_tbl)
        story.append(Spacer(1, 0.12*inch))
        
        # Score boxes row
        score_data = [[
            f"OVERALL SCORE\n{self.risk_score}/100",
            f"Profitability\n{self._fmt(self.ratios['profitability'].get('net_margin'))}%",
            f"Leverage\n{self._fmt(self.ratios['leverage'].get('debt_to_equity'))}x",
            f"Liquidity\n{self._fmt(self.ratios['liquidity'].get('current_ratio'))}x",
            f"Growth\n{self._fmt(self.ratios['growth'].get('revenue_growth'))}%",
            f"Z-Score\n{self._fmt(self.ratios['risk'].get('altman_z_score'))}"
        ]]
        score_tbl = Table(score_data, colWidths=[1.25*inch]*6)
        score_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), BLUE),
            ('TEXTCOLOR', (0,0), (0,0), colors.white),
            ('BACKGROUND', (1,0), (-1,0), LIGHT),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(score_tbl)
        story.append(Spacer(1, 0.15*inch))
        
        # Investment Thesis Section
        story.append(Paragraph("INVESTMENT THESIS", styles['Title3']))
        if 'THESIS' in self.report_sections:
            story.append(Paragraph(self.report_sections['THESIS'], styles['Body']))
        
        story.append(Spacer(1, 0.1*inch))
        
        # Key metrics table
        story.append(Paragraph("KEY FINANCIAL METRICS", styles['Title3']))
        metrics = [
            ['PROFITABILITY', '', '', 'LEVERAGE & RISK', '', ''],
            ['Gross Margin', f"{self._fmt(self.ratios['profitability'].get('gross_margin'))}%", '',
             'Debt/Equity', f"{self._fmt(self.ratios['leverage'].get('debt_to_equity'))}x", ''],
            ['Operating Margin', f"{self._fmt(self.ratios['profitability'].get('operating_margin'))}%", '',
             'Interest Coverage', f"{self._fmt(self.ratios['leverage'].get('interest_coverage'))}x", ''],
            ['Net Margin', f"{self._fmt(self.ratios['profitability'].get('net_margin'))}%", '',
             'CF to Debt', f"{self._fmt(self.ratios['leverage'].get('cash_flow_to_debt'))}", ''],
            ['ROE', f"{self._fmt(self.ratios['profitability'].get('roe'))}%", '',
             'Current Ratio', f"{self._fmt(self.ratios['liquidity'].get('current_ratio'))}x", ''],
            ['ROCE', f"{self._fmt(self.ratios['profitability'].get('roce'))}%", '',
             'Altman Z-Score', f"{self._fmt(self.ratios['risk'].get('altman_z_score'))}", ''],
        ]
        m_tbl = Table(metrics, colWidths=[1.2*inch, 0.8*inch, 0.3*inch, 1.2*inch, 0.8*inch, 0.3*inch])
        m_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (2,0), BLUE),
            ('BACKGROUND', (3,0), (5,0), colors.HexColor('#744210')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('SPAN', (0,0), (2,0)), ('SPAN', (3,0), (5,0)),
            ('BACKGROUND', (0,1), (0,-1), LIGHT),
            ('BACKGROUND', (3,1), (3,-1), LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('ALIGN', (4,0), (4,-1), 'CENTER'),
        ]))
        story.append(m_tbl)
        
        story.append(PageBreak())
        
        # ==================== PAGE 2: ANALYSIS ====================
        
        story.append(Paragraph("SCORE ANALYSIS", styles['Title2']))
        
        # Signal breakdown table
        sig_data = [['Factor', 'Signal', 'Value', 'Buy Threshold', 'Sell Threshold']]
        thresholds = {
            'Risk Score': ('>70', '<40'), 'Revenue Growth': ('>10%', '<0%'), 
            'Net Income Growth': ('>10%', '<0%'), 'ROE': ('>15%', '<10%'),
            'Altman Z-Score': ('>3.0', '<1.81'), 'CF to Debt': ('>0.5', '<0.2'),
            'Net Debt/EBITDA': ('<2x', '>4x'), 'Current Ratio': ('>1.5', '<1.0'),
            'Net Margin': ('>15%', '<5%'), 'ROCE': ('>15%', '<8%')
        }
        
        for name, (sig, val) in self.signal_breakdown.items():
            buy_th, sell_th = thresholds.get(name, ('', ''))
            sig_data.append([name, sig, val, buy_th, sell_th])
        
        sig_tbl = Table(sig_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
        sig_styles = [
            ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]
        for i, (name, (sig, val)) in enumerate(self.signal_breakdown.items(), 1):
            clr = '#c6f6d5' if sig == 'BUY' else '#fed7d7' if sig == 'SELL' else '#fefcbf'
            sig_styles.append(('BACKGROUND', (1, i), (1, i), colors.HexColor(clr)))
        sig_tbl.setStyle(TableStyle(sig_styles))
        story.append(sig_tbl)
        story.append(Spacer(1, 0.1*inch))
        
        # Signal summary
        sum_data = [[f"Bullish: {self.buy_signals}", f"Neutral: {self.hold_signals}", f"Bearish: {self.sell_signals}"]]
        sum_tbl = Table(sum_data, colWidths=[1.7*inch]*3)
        sum_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#c6f6d5')),
            ('BACKGROUND', (1,0), (1,0), colors.HexColor('#fefcbf')),
            ('BACKGROUND', (2,0), (2,0), colors.HexColor('#fed7d7')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOX', (0,0), (-1,-1), 1, DARK_BLUE),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(sum_tbl)
        story.append(Spacer(1, 0.1*inch))
        
        # Charts
        def make_charts():
            fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.2))
            
            # Pie
            ax1 = axes[0]
            sizes = [self.buy_signals, self.hold_signals, self.sell_signals]
            clrs = ['#48bb78', '#ecc94b', '#fc8181']
            ax1.pie(sizes, labels=[f'BUY\n({self.buy_signals})', f'HOLD\n({self.hold_signals})', f'SELL\n({self.sell_signals})'], 
                   colors=clrs, autopct='%1.0f%%', startangle=90, textprops={'fontsize': 8})
            ax1.set_title('Signal Distribution', fontsize=10, fontweight='bold', color='#1a365d')
            
            # Bar
            ax2 = axes[1]
            metrics_names = ['Gross\nMargin', 'Net\nMargin', 'ROE', 'ROCE']
            vals = [
                self.ratios['profitability'].get('gross_margin', 0) or 0,
                self.ratios['profitability'].get('net_margin', 0) or 0,
                self.ratios['profitability'].get('roe', 0) or 0,
                self.ratios['profitability'].get('roce', 0) or 0,
            ]
            bar_clrs = ['#4299e1' if v >= 15 else '#ecc94b' if v >= 5 else '#fc8181' for v in vals]
            bars = ax2.bar(metrics_names, vals, color=bar_clrs, edgecolor='#2d3748', linewidth=0.5)
            ax2.set_ylabel('%', fontsize=8)
            ax2.set_title('Profitability Profile', fontsize=10, fontweight='bold', color='#1a365d')
            ax2.tick_params(labelsize=7)
            ax2.axhline(15, color='#48bb78', linestyle='--', alpha=0.5)
            for bar, v in zip(bars, vals):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{v:.1f}%', ha='center', fontsize=7)
            
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
            plt.close()
            buf.seek(0)
            return buf
        
        try:
            chart_buf = make_charts()
            story.append(Image(chart_buf, width=6.8*inch, height=2.1*inch))
        except Exception as e:
            print(f"    Charts error: {e}")
        
        # Profitability Analysis
        story.append(Paragraph("PROFITABILITY ANALYSIS", styles['Title3']))
        if 'PROFITABILITY' in self.report_sections:
            story.append(Paragraph(self.report_sections['PROFITABILITY'], styles['Body']))
        
        # Leverage Analysis  
        story.append(Paragraph("LEVERAGE & SOLVENCY", styles['Title3']))
        if 'LEVERAGE' in self.report_sections:
            story.append(Paragraph(self.report_sections['LEVERAGE'], styles['Body']))
        
        story.append(PageBreak())
        
        # ==================== PAGE 3: FORECAST ====================
        
        story.append(Paragraph("FINANCIAL FORECAST", styles['Title2']))
        story.append(Paragraph("4-Year projections based on historical trends | Bull / Base / Bear scenarios", styles['Small']))
        story.append(Spacer(1, 0.1*inch))
        
        if self.forecast:
            years = self.forecast_years if self.forecast_years else ['Y1', 'Y2', 'Y3', 'Y4']
            
            fc_data = [['Metric', 'Scenario'] + years]
            items = [('revenue', 'Revenue ($B)'), ('net_income', 'Net Income ($B)'), 
                    ('free_cash_flow', 'Free Cash Flow ($B)'), ('total_debt', 'Total Debt ($B)')]
            
            for key, name in items:
                if key in self.forecast:
                    for sc in ['bull', 'base', 'bear']:
                        if sc in self.forecast[key]:
                            row = [name if sc == 'bull' else '', sc.upper()]
                            row += [f"{v/1e9:.1f}" for v in self.forecast[key][sc]]
                            fc_data.append(row)
            
            if len(fc_data) > 1:
                fc_tbl = Table(fc_data, colWidths=[1.3*inch, 0.7*inch] + [0.85*inch]*4)
                fc_styles = [
                    ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                ]
                for i, row in enumerate(fc_data[1:], 1):
                    if len(row) > 1:
                        if row[1] == 'BULL':
                            fc_styles.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#c6f6d5')))
                        elif row[1] == 'BEAR':
                            fc_styles.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#fed7d7')))
                        elif row[1] == 'BASE':
                            fc_styles.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#bee3f8')))
                fc_tbl.setStyle(TableStyle(fc_styles))
                story.append(fc_tbl)
            
            # Forecast chart
            def make_fc_chart():
                fig, ax = plt.subplots(figsize=(6, 2.3))
                if 'revenue' in self.forecast:
                    yrs = list(range(1, 5))
                    proj = self.forecast['revenue']
                    ax.fill_between(yrs, [v/1e9 for v in proj['bear']], [v/1e9 for v in proj['bull']], alpha=0.2, color='#4299e1')
                    ax.plot(yrs, [v/1e9 for v in proj['base']], 'o-', color='#2c5282', lw=2, label='Base')
                    ax.plot(yrs, [v/1e9 for v in proj['bull']], '--', color='#48bb78', lw=1.5, label='Bull')
                    ax.plot(yrs, [v/1e9 for v in proj['bear']], '--', color='#fc8181', lw=1.5, label='Bear')
                    ax.set_xlabel('Year', fontsize=9)
                    ax.set_ylabel('Revenue ($B)', fontsize=9)
                    ax.set_title('Revenue Projection', fontsize=10, fontweight='bold', color='#1a365d')
                    ax.legend(fontsize=7)
                    ax.grid(alpha=0.3)
                    ax.set_xticks(yrs)
                    ax.set_xticklabels(years)
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
                plt.close()
                buf.seek(0)
                return buf
            
            try:
                fc_chart = make_fc_chart()
                story.append(Spacer(1, 0.1*inch))
                story.append(Image(fc_chart, width=5.5*inch, height=2.1*inch))
            except:
                pass
        
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("GROWTH OUTLOOK", styles['Title3']))
        if 'GROWTH' in self.report_sections:
            story.append(Paragraph(self.report_sections['GROWTH'], styles['Body']))
        
        story.append(PageBreak())
        
        # ==================== PAGE 4: RISKS & CONCLUSION ====================
        
        story.append(Paragraph("RISK ASSESSMENT", styles['Title2']))
        
        # Risk gauge
        def make_risk_gauge():
            fig, ax = plt.subplots(figsize=(5.5, 1.2))
            ax.barh([0], [40], color='#fed7d7', height=0.5)
            ax.barh([0], [30], left=40, color='#fefcbf', height=0.5)
            ax.barh([0], [30], left=70, color='#c6f6d5', height=0.5)
            clr = '#48bb78' if self.risk_score >= 70 else '#ecc94b' if self.risk_score >= 40 else '#fc8181'
            ax.scatter([self.risk_score], [0], s=250, c=clr, edgecolors='#1a365d', linewidths=2, zorder=5)
            ax.text(self.risk_score, 0, f'{self.risk_score}', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
            ax.set_xlim(0, 100)
            ax.set_ylim(-0.4, 0.4)
            ax.set_yticks([])
            ax.set_title(f'Financial Health Score: {self.risk_rating}', fontsize=10, fontweight='bold', color='#1a365d')
            ax.text(20, 0.3, 'HIGH RISK', fontsize=7, ha='center', color='#c53030')
            ax.text(55, 0.3, 'MODERATE', fontsize=7, ha='center', color='#b7791f')
            ax.text(85, 0.3, 'LOW RISK', fontsize=7, ha='center', color='#276749')
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
            plt.close()
            buf.seek(0)
            return buf
        
        try:
            rg = make_risk_gauge()
            story.append(Image(rg, width=5*inch, height=1.1*inch))
        except:
            pass
        
        story.append(Spacer(1, 0.1*inch))
        
        # Risks and Catalysts side by side concept - but sequential for simplicity
        story.append(Paragraph("KEY RISKS", styles['Title3']))
        if 'RISKS' in self.report_sections:
            for line in self.report_sections['RISKS'].split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    story.append(Paragraph(f"• {line[1:].strip()}", styles['Bullet']))
                elif line:
                    story.append(Paragraph(line, styles['Body']))
        
        story.append(Paragraph("POTENTIAL CATALYSTS", styles['Title3']))
        if 'CATALYSTS' in self.report_sections:
            for line in self.report_sections['CATALYSTS'].split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    story.append(Paragraph(f"• {line[1:].strip()}", styles['Bullet']))
                elif line:
                    story.append(Paragraph(line, styles['Body']))
        
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph("INVESTMENT CONCLUSION", styles['Title2']))
        if 'CONCLUSION' in self.report_sections:
            story.append(Paragraph(self.report_sections['CONCLUSION'], styles['Body']))
        
        # Final verdict box
        story.append(Spacer(1, 0.1*inch))
        final = [[self.recommendation, f"Target: ${self.target_price:,.2f}", f"Return: {self.upside:+.1f}%", f"Confidence: {self.confidence:.0f}%"]]
        f_tbl = Table(final, colWidths=[1.2*inch, 1.7*inch, 1.2*inch, 1.3*inch])
        f_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), rec_color),
            ('TEXTCOLOR', (0,0), (0,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (0,0), 16),
            ('FONTSIZE', (1,0), (-1,0), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOX', (0,0), (-1,-1), 1.5, DARK_BLUE),
            ('LINEAFTER', (0,0), (-2,0), 0.5, colors.HexColor('#cbd5e0')),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(f_tbl)
        
        # Disclaimer
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("DISCLAIMER", styles['Small']))
        story.append(Paragraph(
            "This report is generated for educational purposes as part of MSc AI Agents in Asset Management (Track A: Fundamental Analyst). "
            "Not investment advice. Past performance doesn't guarantee future results. Conduct independent due diligence.",
            styles['Small']
        ))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"Generated: {self.report_date} | Model: GPT-4o-mini | Fundamental Analyst Agent v1.0", styles['Footer']))
        
        doc.build(story)
        return path
    
    # ==================== CONSOLE ====================
    
    def _print_summary(self):
        print(f"\n{'='*60}")
        print(f"  {self.ticker}: {self.recommendation} | {self.confidence:.0f}% | ${self.target_price:,.2f}")
        print(f"{'='*60}")
    
    def analyze(self, ticker: str, refresh: bool = False):
        self.ticker = ticker.upper()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_date = datetime.now().strftime("%B %d, %Y")
        
        print(f"\n{'='*60}")
        print(f"  FUNDAMENTAL ANALYST AGENT")
        print(f"  Analyzing: {self.ticker}")
        print(f"{'='*60}")
        
        self._collect_data(self.ticker, refresh)
        self._calculate_ratios()
        self._run_forecast()
        self._calculate_score()
        self._generate_ai_report()
        self._print_summary()
        files = self._export()
        
        print(f"\n  ✓ COMPLETE\n")
        return files


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py TICKER [--refresh]")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    refresh = "--refresh" in sys.argv
    
    agent = FundamentalAgent()
    agent.analyze(ticker, refresh=refresh)