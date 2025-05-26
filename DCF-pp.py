#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 11:57:41 2025

@author: peterdu
"""

import yfinance as yf

#%%

# SUBJECT COMPANY
ticker = 'NKE'

# RANGE ASSUMPTIONS
terminal_growth = 0.015     # 1.5%
exit_multiple = 16.08       # EV/EBITDA
growth_rate = 0.02          # 3% annual FCF growth
projection_years = 5
risk_free = 0.04543         # 10-year Treasury
market_return = 0.09043     # Expected market return
tax_rate = 0.165            # Effective tax rate
cost_of_debt = 0.05         # Pre-tax cost of debt
beta = 1.01                 # Beta

# DATA COLLECTION
stock = yf.Ticker(ticker)
info = stock.info

# Try to safely get data, with fallbacks
try:
    fcf_ttm = info.get("freeCashflow", info["marketCap"] * 0.05)
    ebitda_ttm = info.get("ebitda", None)
    shares_outstanding = info["sharesOutstanding"]
    debt = info.get("totalDebt", 0)
    market_cap = info["marketCap"]
    current_price = stock.info['regularMarketPrice']
    print(f"Using scraped values for {ticker}...")
except:
    raise ValueError("Could not fetch complete data from yfinance.")

# FCF PROJECTIONS
fcfs = []
fcf = fcf_ttm
for _ in range(projection_years):
    fcf *= (1 + growth_rate)
    fcfs.append(fcf)

# WACC

equity = market_cap
debt = debt
value = equity + debt

# Cost of equity by CAPM
cost_of_equity = risk_free + beta * (market_return - risk_free)

# WACC
wacc = (equity / value) * cost_of_equity + (debt / value) * cost_of_debt * (1 - tax_rate)

# TV CALCULATIONS
# PERP METHOD
tv_perp = fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)

# EXIT MULTIPLE METHOD
if ebitda_ttm:
    ebitda_proj = ebitda_ttm * (1 + growth_rate) ** projection_years
    tv_exit = ebitda_proj * exit_multiple
else:
    tv_exit = tv_perp

# TV AVERAGED OUT
tv_avg = (tv_perp + tv_exit) / 2

# DISCOUNTING
discounted_fcfs = [fcfs[i] / ((1 + wacc) ** (i + 1)) for i in range(projection_years)]
discounted_tv = tv_avg / ((1 + wacc) ** projection_years)

# VALUATIONS FINAL
enterprise_value = sum(discounted_fcfs) + discounted_tv
equity_value = enterprise_value - debt
share_price = equity_value / shares_outstanding

# OUTPUT RESULTS
print("--- WACC CALCULATION ---")
print(f"Cost of Equity (CAPM): {cost_of_equity:.4f}")
print(f"Cost of Debt (after-tax): {cost_of_debt * (1 - tax_rate):.4f}")
print(f"WACC: {wacc:.4f}")
print("\n--- DCF VALUATION RESULTS ---")
print(f"Ticker: {ticker}")
print(f"Projected FCFs: {[round(f/1e6, 2) for f in fcfs]} (in millions)")
print(f"Terminal Value (avg): ${tv_avg:,.0f}")
print(f"Discounted TV: ${discounted_tv:,.0f}")
print(f"Enterprise Value: ${enterprise_value:,.0f}")
print(f"Equity Value: ${equity_value:,.0f}")
print(f"Current Share Price: ${current_price:.2f}")
print(f"Intrinsic Share Price: ${share_price:.2f}")

