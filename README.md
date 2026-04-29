# TradingView to Alpaca Webhook Receiver

This tool connects TradingView alerts to your Alpaca brokerage account so that when a chart alert fires on TradingView, it automatically places a trade on Alpaca — no manual clicking required.

## What it does

1. TradingView fires an alert on your chart (e.g. an EMA crossover).
2. TradingView sends a message to this tool over the internet.
3. This tool checks if the trade is safe to place (market open, account not blocked, no duplicate position, daily limit not hit).
4. If all checks pass, the order is submitted to Alpaca.
5. The result is logged so you can see what happened and why.

By default it runs in **paper trading mode**, meaning fake money only. You have to explicitly turn on live trading.

---

## What you need before starting

- A computer running Windows, macOS, or Linux
- **Python 3.11 or newer** — download from [python.org](https://www.python.org/downloads/)
  - During install on Windows, tick the box that says **"Add Python to PATH"**
- **An Alpaca account** — sign up free at [alpaca.markets](https://alpaca.markets)
  - You need a paper trading API key to start (no real money required)
  - Get your keys from: Alpaca dashboard → API Keys → Generate New Key
- **A TradingView account** — free tier works, but webhook alerts require a **paid plan** (Essential or higher)
- A terminal or command prompt (PowerShell on Windows, Terminal on Mac/Linux)

---

## How the pieces fit together

```
TradingView alert fires
        ↓
Sends JSON to your public URL  ← you need a public URL (see setup guide)
        ↓
This tool receives it and checks risk rules
        ↓
Submits order to Alpaca if checks pass
        ↓
Returns submitted / skipped / error
```

> **Important:** TradingView sends webhooks over the internet, so your computer
> needs a public URL. During development, use a free tunnel tool like
> [ngrok](https://ngrok.com) to expose your local machine. For permanent
> use, deploy to a cloud server or VPS.

---

## Quick start

Full step-by-step instructions are in the [setup and operations guide](tradingview_alpaca/README.md).

The running project assessment and analysis log is in [prompts/project-analysis/project_analysis.md](prompts/project-analysis/project_analysis.md).

---

## Project file overview

You do not need to touch any of these files to get started, but here is what each one does:

| File | What it does |
|---|---|
| `tradingview_alpaca/main.py` | The web server that receives alerts |
| `tradingview_alpaca/config.py` | Reads your settings from the `.env` file |
| `tradingview_alpaca/models.py` | Validates the shape of incoming alerts |
| `tradingview_alpaca/alpaca_client.py` | Talks to the Alpaca API |
| `tradingview_alpaca/order_manager.py` | Builds and submits orders |
| `tradingview_alpaca/risk_filter.py` | Runs safety checks before any order |
| `tradingview_alpaca/logger.py` | Records what happened and when |
| `tradingview_alpaca/tests/` | Automated tests to confirm everything works |

---

## Safety defaults

- Paper trading is **on by default**. No real money is touched unless you explicitly set `PAPER_TRADING=false`.
- Orders are capped at a maximum quantity per trade.
- A daily order limit acts as a circuit breaker.
- Both limits are set in your `.env` file and can be adjusted without touching any code.

---

## Resources

- [Alpaca Python SDK](https://alpaca.markets/sdks/python/)
- [Alpaca paper trading](https://docs.alpaca.markets/docs/paper-trading)
- [Alpaca Trading API reference](https://docs.alpaca.markets/reference/trading-api)
- [TradingView webhooks](https://www.tradingview.com/support/solutions/43000529348-about-webhooks/)
- [TradingView alerts guide](https://www.tradingview.com/support/folders/43000560104-alerts/)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [ngrok (free tunnel for local testing)](https://ngrok.com)
