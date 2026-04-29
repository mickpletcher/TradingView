# TradingView Automation Projects

This repo contains TradingView automation modules that receive TradingView alerts and route them into different downstream systems.

Right now the repo includes:

- `tradingview_alpaca` for direct trade execution through Alpaca
- `tradingview_n8n` for routing alerts into an n8n workflow graph
- root-level planning notes such as `future-upgrades.md` for broader repo expansion ideas

Each subproject should have its own local analysis note so future changes can start from a concise snapshot instead of a full re-read.

## What the repo does

1. TradingView fires an alert on your chart (e.g. an EMA crossover).
2. TradingView sends a message to one of the repo's webhook targets over the internet.
3. That target either routes the alert into an automation system or executes a broker action.
4. The result is then logged, routed, or acted on downstream.

The `tradingview_alpaca` module runs in **paper trading mode** by default, meaning fake money only. You have to explicitly turn on live trading.

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

## Modules

- [tradingview_alpaca](tradingview_alpaca/README.md)
  Direct execution module for sending TradingView alerts to Alpaca with validation and safety checks.

- [tradingview_alpaca/project-analysis.md](tradingview_alpaca/project-analysis.md)
  Quick-reference analysis for the Alpaca subproject, including architecture, risks, validation status, and editing guidance.

- [tradingview_n8n](tradingview_n8n/README.md)
  Automation-routing module for sending TradingView alerts into n8n so they can notify, log, enrich, or fan out to other systems.

- [tradingview_n8n/project-analysis.md](tradingview_n8n/project-analysis.md)
  Quick-reference analysis for the n8n subproject, including scope, design intent, current gaps, and recommended next steps.

## Quick start

- For broker execution with Alpaca, start with the [setup and operations guide](tradingview_alpaca/README.md).
- For automation routing with n8n, start with [tradingview_n8n/README.md](tradingview_n8n/README.md).
- For subproject-level context before making changes, start with [tradingview_alpaca/project-analysis.md](tradingview_alpaca/project-analysis.md) or [tradingview_n8n/project-analysis.md](tradingview_n8n/project-analysis.md).

The repo-wide expansion backlog is in [future-upgrades.md](future-upgrades.md).

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
| `tradingview_alpaca/project-analysis.md` | Quick analysis snapshot for the Alpaca module |
| `tradingview_alpaca/tests/` | Automated tests to confirm everything works |
| `tradingview_n8n/README.md` | Setup and design notes for the n8n routing module |
| `tradingview_n8n/project-analysis.md` | Quick analysis snapshot for the n8n module |
| `tradingview_n8n/tradingview-message-example.json` | Example TradingView alert payload for n8n workflows |
| `future-upgrades.md` | Root-level local roadmap for additional TradingView subprojects |

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
