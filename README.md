# 📈 CLI Stock Screener

A terminal-based stock screener that pulls live data from Yahoo Finance (free, no API key) and filters stocks by P/E ratio, dividend yield, market cap, and daily movement.

## 🚀 Features
- Live stock data via `yfinance` (no API key needed)
- Filter by P/E ratio, dividend yield, market cap, gainers/losers
- Built-in watchlists: Tech, India (NSE), ETFs, Finance
- Sort by P/E, dividend, market cap, price change
- Beautiful terminal table with 52-week range, beta, volume
- Summary stats: gainer/loser count, average daily change

## 🛠 Tech Stack
- Python 3.10+
- `yfinance` — Yahoo Finance data
- `pandas` — data handling
- `tabulate` — pretty terminal tables



## 🖥 Usage
```bash
# Screen the default sample list
python screener.py

# Screen specific tickers
python screener.py AAPL TSLA NVDA MSFT

# Use the India (NSE) watchlist
python screener.py --list india

# Filter: P/E under 25, paying dividends, sort by dividend yield
python screener.py --list tech --max-pe 25 --min-div 0.5 --sort div

# Show only today's gainers in the tech list
python screener.py --list tech --gainers

# Small caps only (under $10B)
python screener.py AAPL TSLA NVDA --max-cap 10

# Sort by P/E ratio
python screener.py --list finance --sort pe
```

## 📊 Available Watchlists
| List | Tickers |
|---|---|
| `tech` | AAPL, MSFT, GOOGL, META, NVDA, TSLA... |
| `india` | RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS... |
| `etf` | SPY, QQQ, VTI, ARKK, GLD... |
| `finance` | JPM, BAC, GS, MS, V, MA... |

## ⚠️ Disclaimer
This tool is for educational/informational purposes only. Not financial advice.

## 📄 License
MIT
