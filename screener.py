"""
CLI Stock Screener 📈
Filter and rank stocks by fundamentals using Yahoo Finance (free, no API key).
Screen by P/E ratio, market cap, volume, dividend yield, and more.

Requirements: pip install yfinance pandas tabulate
"""

import argparse
import sys
from datetime import datetime

try:
    import yfinance as yf
    import pandas as pd
    from tabulate import tabulate
except ImportError:
    print("Missing packages. Run: pip install yfinance pandas tabulate")
    sys.exit(1)

# ── ANSI ──────────────────────────────────────────────────────────────────────
R   = "\033[0m"
B   = "\033[1m"
G   = "\033[32m"
RE  = "\033[31m"
Y   = "\033[33m"
C   = "\033[36m"
DIM = "\033[2m"

# ── Default watchlists ────────────────────────────────────────────────────────
WATCHLISTS = {
    "tech":    ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA", "AMZN", "ADBE", "CRM", "INTC"],
    "india":   ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS", "LT.NS", "ICICIBANK.NS", "BAJFINANCE.NS"],
    "etf":     ["SPY", "QQQ", "VTI", "ARKK", "GLD", "IWM", "XLF", "SCHD"],
    "finance": ["JPM", "BAC", "GS", "MS", "WFC", "V", "MA", "AXP"],
    "sample":  ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"],
}

# ── Fetch stock data ──────────────────────────────────────────────────────────

def fetch_stock(ticker: str) -> dict | None:
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1d")

        price = info.get("currentPrice") or info.get("regularMarketPrice") or (
            hist["Close"].iloc[-1] if not hist.empty else None
        )
        if price is None:
            return None

        change_pct = info.get("regularMarketChangePercent", 0) or 0

        return {
            "Ticker":    ticker.upper(),
            "Name":      (info.get("shortName") or ticker)[:20],
            "Price":     round(price, 2),
            "Chg%":      round(change_pct, 2),
            "P/E":       round(info.get("trailingPE") or 0, 1) or "—",
            "EPS":       round(info.get("trailingEps") or 0, 2) or "—",
            "Mkt Cap":   _fmt_cap(info.get("marketCap")),
            "Div%":      round(info.get("dividendYield") or 0, 3) * 100 or "—",
            "52W Hi":    round(info.get("fiftyTwoWeekHigh") or 0, 2),
            "52W Lo":    round(info.get("fiftyTwoWeekLow") or 0, 2),
            "Volume":    _fmt_vol(info.get("volume")),
            "Beta":      round(info.get("beta") or 0, 2) or "—",
            "_price":    price,
            "_chg":      change_pct,
            "_pe":       info.get("trailingPE") or 999,
            "_cap":      info.get("marketCap") or 0,
            "_div":      (info.get("dividendYield") or 0) * 100,
            "_vol":      info.get("volume") or 0,
        }
    except Exception as e:
        return None

def _fmt_cap(cap) -> str:
    if not cap:
        return "—"
    if cap >= 1e12:
        return f"${cap/1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap/1e9:.1f}B"
    return f"${cap/1e6:.0f}M"

def _fmt_vol(vol) -> str:
    if not vol:
        return "—"
    if vol >= 1e6:
        return f"{vol/1e6:.1f}M"
    if vol >= 1e3:
        return f"{vol/1e3:.0f}K"
    return str(vol)

# ── Screening ─────────────────────────────────────────────────────────────────

def screen(stocks: list[dict], args) -> list[dict]:
    filtered = []
    for s in stocks:
        if args.max_pe and s["_pe"] != 999 and s["_pe"] > args.max_pe:
            continue
        if args.min_pe and s["_pe"] < args.min_pe:
            continue
        if args.min_div and s["_div"] < args.min_div:
            continue
        if args.min_cap and s["_cap"] < args.min_cap * 1e9:
            continue
        if args.max_cap and s["_cap"] > args.max_cap * 1e9:
            continue
        if args.gainers and s["_chg"] <= 0:
            continue
        if args.losers and s["_chg"] >= 0:
            continue
        filtered.append(s)

    sort_key = {
        "pe":     lambda x: x["_pe"],
        "div":    lambda x: -x["_div"],
        "cap":    lambda x: -x["_cap"],
        "change": lambda x: -x["_chg"],
        "price":  lambda x: x["_price"],
    }.get(args.sort, lambda x: -x["_cap"])

    return sorted(filtered, key=sort_key)

# ── Display ───────────────────────────────────────────────────────────────────

def colorize_chg(val) -> str:
    if isinstance(val, str):
        return val
    return f"{G}+{val}%{R}" if val > 0 else f"{RE}{val}%{R}" if val < 0 else f"{val}%"

def display(stocks: list[dict], title: str):
    if not stocks:
        print(f"\n{Y}No stocks match your criteria.{R}")
        return

    print(f"\n{C}{B}  📊 {title}{R}  {DIM}({len(stocks)} results — {datetime.now().strftime('%H:%M')}){R}\n")

    display_rows = []
    for s in stocks:
        chg_str = f"+{s['Chg%']}%" if s["_chg"] > 0 else f"{s['Chg%']}%"
        display_rows.append({
            "Ticker":   s["Ticker"],
            "Name":     s["Name"],
            "Price":    f"${s['Price']}",
            "Chg%":     chg_str,
            "P/E":      s["P/E"],
            "EPS":      s["EPS"],
            "Mkt Cap":  s["Mkt Cap"],
            "Div%":     f"{s['Div%']}%" if s["Div%"] != "—" else "—",
            "52W Range":f"{s['52W Lo']} – {s['52W Hi']}",
            "Volume":   s["Volume"],
            "Beta":     s["Beta"],
        })

    print(tabulate(display_rows, headers="keys", tablefmt="rounded_outline"))
    print()

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="📈 CLI Stock Screener — filter stocks by fundamentals"
    )
    parser.add_argument("tickers", nargs="*", help="Ticker symbols (e.g. AAPL TSLA)")
    parser.add_argument("--list", choices=WATCHLISTS.keys(), default="sample",
                        help="Use a built-in watchlist")
    parser.add_argument("--max-pe",  type=float, help="Max P/E ratio")
    parser.add_argument("--min-pe",  type=float, help="Min P/E ratio")
    parser.add_argument("--min-div", type=float, help="Min dividend yield %%")
    parser.add_argument("--min-cap", type=float, help="Min market cap (billions)")
    parser.add_argument("--max-cap", type=float, help="Max market cap (billions)")
    parser.add_argument("--gainers", action="store_true", help="Only show gainers today")
    parser.add_argument("--losers",  action="store_true", help="Only show losers today")
    parser.add_argument("--sort", choices=["pe","div","cap","change","price"],
                        default="cap", help="Sort by (default: market cap)")

    args = parser.parse_args()

    tickers = args.tickers if args.tickers else WATCHLISTS[args.list]
    tickers = [t.upper() for t in tickers]

    print(f"\n{B}Fetching data for {len(tickers)} stocks...{R}")
    print(f"{DIM}(This may take a few seconds){R}\n")

    stocks = []
    for i, ticker in enumerate(tickers):
        print(f"  [{i+1}/{len(tickers)}] {ticker}...", end="\r")
        data = fetch_stock(ticker)
        if data:
            stocks.append(data)

    screened = screen(stocks, args)

    filters = []
    if args.max_pe:   filters.append(f"P/E ≤ {args.max_pe}")
    if args.min_pe:   filters.append(f"P/E ≥ {args.min_pe}")
    if args.min_div:  filters.append(f"Div% ≥ {args.min_div}%")
    if args.min_cap:  filters.append(f"Cap ≥ ${args.min_cap}B")
    if args.gainers:  filters.append("Gainers only")
    if args.losers:   filters.append("Losers only")
    title = f"Screen Results — {' | '.join(filters) if filters else 'No filters'}"

    display(screened, title)

    # Quick summary
    if screened:
        gainers = sum(1 for s in screened if s["_chg"] > 0)
        losers  = sum(1 for s in screened if s["_chg"] < 0)
        avg_chg = sum(s["_chg"] for s in screened) / len(screened)
        print(f"  {G}▲ Gainers: {gainers}{R}  {RE}▼ Losers: {losers}{R}  "
              f"Avg change: {G if avg_chg >= 0 else RE}{avg_chg:+.2f}%{R}\n")

if __name__ == "__main__":
    main()
