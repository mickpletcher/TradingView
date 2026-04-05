# Setup and Operations Guide

This guide walks you through everything from a fresh clone to receiving your first live alert from TradingView.

---

## Step 1 — Get your Alpaca API keys

1. Go to [alpaca.markets](https://alpaca.markets) and create a free account.
2. From the dashboard, click **Paper Trading** in the left sidebar.
3. Click **API Keys** → **Generate New Key**.
4. Copy both the **API Key ID** and the **Secret Key** and save them somewhere safe.
   You will not be able to see the secret key again after closing that window.

> Paper trading uses fake money. You can test everything here without any financial risk.
> When you are ready for live trading, generate a separate set of keys from the Live Trading section.

---

## Step 2 — Set up the project on your computer

Open PowerShell (Windows) or Terminal (Mac/Linux) and run these commands one at a time.

**Navigate into the project folder:**

```powershell
cd path\to\TradingView\tradingview_alpaca
```

Replace `path\to\TradingView` with wherever you cloned or downloaded this repository.

**Create a virtual environment:**

```powershell
python -m venv .venv
```

A virtual environment is an isolated space for this project's packages. It keeps things clean and prevents conflicts with other Python projects on your machine.

**Activate the virtual environment:**

```powershell
# Windows
.\.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

You should see `(.venv)` appear at the start of your terminal prompt. This means the virtual environment is active. Always activate it before running the project.

**Install the required packages:**

```powershell
pip install -r requirements.txt
```

This downloads all the libraries the project needs (FastAPI, Alpaca SDK, etc.).

---

## Step 3 — Create your settings file

**Copy the example settings file:**

```powershell
Copy-Item .env.example .env
```

This creates a file called `.env` in the same folder. It holds your private settings and API keys. **Never commit this file to GitHub.**

**Open `.env` in a text editor and fill in your values:**

```env
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
PAPER_TRADING=true
WEBHOOK_SECRET=change_me_to_a_long_random_string
MAX_ORDER_QTY=100
MAX_DAILY_ORDERS=20
RISK_CHECK_TIMEOUT_SECONDS=8
ORDER_SUBMIT_TIMEOUT_SECONDS=12
```

**What each setting means:**

| Setting | What it does |
|---|---|
| `ALPACA_API_KEY` | Your Alpaca API key ID (from Step 1) |
| `ALPACA_SECRET_KEY` | Your Alpaca secret key (from Step 1) |
| `PAPER_TRADING` | Set to `true` for fake money, `false` for real money |
| `WEBHOOK_SECRET` | A password you invent — TradingView must send this exact value or the alert is rejected. Make it long and random, e.g. `my-super-secret-key-2026` |
| `MAX_ORDER_QTY` | Maximum number of shares allowed per order |
| `MAX_DAILY_ORDERS` | Maximum total orders per day — acts as an emergency brake |
| `RISK_CHECK_TIMEOUT_SECONDS` | How long to wait for Alpaca risk checks before giving up |
| `ORDER_SUBMIT_TIMEOUT_SECONDS` | How long to wait for an order to submit before giving up |

---

## Step 4 — Start the server

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see output like:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**Check it is working:**

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok", "paper": true }
```

The `--reload` flag restarts the server automatically when you save a file. Remove it for production use.

---

## Step 5 — Expose your server to the internet

TradingView sends webhooks over the internet, so your local server needs a public URL.

**For testing, use ngrok (free):**

1. Download ngrok from [ngrok.com](https://ngrok.com) and create a free account.
2. Follow their setup instructions to authenticate ngrok on your machine.
3. Run this while your server is already running:

```powershell
ngrok http 8000
```

4. ngrok will show you a public URL like `https://abc123.ngrok-free.app`.
5. Your webhook URL will be: `https://abc123.ngrok-free.app/webhook`

> The ngrok URL changes each time you restart ngrok on the free plan. For a permanent URL, use a paid ngrok plan or deploy to a cloud server.

**For permanent use:**

Deploy to any cloud provider (Railway, Render, Fly.io, DigitalOcean, etc.) and point your domain or the provider's URL at port 8000. The startup command is:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Step 6 — Configure TradingView

> TradingView webhook alerts require a **paid plan** (Essential or higher).

1. Open TradingView and go to your chart.
2. Click the **Alerts** button (clock icon) → **Create Alert**.
3. Set your alert condition (e.g. EMA crossover, RSI threshold, etc.).
4. Scroll down to **Notifications** and enable **Webhook URL**.
5. Enter your public URL: `https://your-url-here/webhook`
6. In the **Message** box, paste this JSON exactly — replace the values on the `side`, `qty`, and `strategy` lines to match your alert:

```json
{
  "symbol":   "{{ticker}}",
  "side":     "buy",
  "qty":      10,
  "strategy": "ema_cross",
  "price":    {{close}},
  "interval": "{{interval}}",
  "time":     "{{timenow}}"
}
```

- `{{ticker}}`, `{{close}}`, `{{interval}}`, and `{{timenow}}` are TradingView variables that get filled in automatically when the alert fires.
- Change `"side"` to `"buy"` or `"sell"` as appropriate.
- Change `"qty"` to the number of shares you want to trade.
- Change `"strategy"` to any label you want (used for logging only).

7. Go to the **Settings** tab of the alert and add this custom header so the tool can verify the alert came from you:

```
X-Webhook-Secret: your_webhook_secret_here
```

Replace `your_webhook_secret_here` with the exact value you set as `WEBHOOK_SECRET` in your `.env` file.

8. Save the alert. When it fires, the order will be placed automatically.

---

## Run the tests

Before using the tool for real, confirm everything is wired up correctly:

```powershell
pytest -q
```

All tests should pass. If any fail, check that your virtual environment is active and packages are installed.

---

## Send a manual test alert

You can simulate a TradingView alert from PowerShell to test the full flow without waiting for your chart condition to trigger:

```powershell
$headers = @{ "X-Webhook-Secret" = "your_webhook_secret_here" }
$body = @{
  symbol   = "AAPL"
  side     = "buy"
  qty      = 10
  strategy = "ema_cross"
  price    = 201.34
  interval = "5"
  time     = "2026-04-04T14:30:00Z"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/webhook -Headers $headers -Body $body -ContentType "application/json"
```

Replace `your_webhook_secret_here` with your actual `WEBHOOK_SECRET` value.

A successful response looks like:

```json
{
  "status": "submitted",
  "order_id": "abc-123-...",
  "symbol": "AAPL",
  "side": "buy",
  "qty": 10,
  "reason": null
}
```

If the market is closed, you will get `"status": "skipped"` with `"reason": "market is closed"` — that is expected behaviour.

---

## Paper trading vs live trading

Paper trading is on by default and uses a simulated account with fake money. Nothing real happens.

To switch modes, edit your `.env` file:

```env
# Paper mode (safe — fake money)
PAPER_TRADING=true

# Live mode (real money — be careful)
PAPER_TRADING=false
```

When switching to live mode, make sure you are also using your **live API keys**, not your paper keys. They are different key pairs on Alpaca.

---

## Troubleshooting

**`401 Unauthorized` response**
The `X-Webhook-Secret` header is missing or does not match your `WEBHOOK_SECRET` setting. Double-check both values match exactly, including capitalisation.

**`422 Unprocessable Entity` response**
The JSON payload is malformed or missing a required field. Check that `symbol`, `side`, `qty`, and `strategy` are all present and correctly typed.

**`status: "skipped"` with reason `"market is closed"`**
The US stock market is not open right now. Alpaca only accepts orders during market hours (Monday–Friday, 9:30 AM – 4:00 PM US Eastern Time). This is expected behaviour.

**`status: "skipped"` with reason `"already long this symbol"`**
You already have an open buy position for this symbol. The risk filter blocked a duplicate entry.

**`status: "skipped"` with reason `"daily order limit of X reached"`**
You have hit the `MAX_DAILY_ORDERS` limit for today. Increase the limit in your `.env` file or wait until tomorrow (resets at midnight UTC).

**`status: "error"` with Alpaca-related reason**
Check that your API keys are correct, your Alpaca account is active and not restricted, and that your machine can reach the internet.

**`(.venv)` is not showing in my terminal**
Your virtual environment is not active. Run `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Mac/Linux) from the `tradingview_alpaca` folder.

**`ModuleNotFoundError` when starting the server**
Your virtual environment is not active, or you have not run `pip install -r requirements.txt` yet.

---

## Resources

- [Alpaca Python SDK](https://alpaca.markets/sdks/python/)
- [Alpaca paper trading](https://docs.alpaca.markets/docs/paper-trading)
- [Alpaca Trading API reference](https://docs.alpaca.markets/reference/trading-api)
- [TradingView webhooks](https://www.tradingview.com/support/solutions/43000529348-about-webhooks/)
- [TradingView alerts guide](https://www.tradingview.com/support/folders/43000560104-alerts/)
- [ngrok — free local tunnel](https://ngrok.com)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [Uvicorn settings](https://www.uvicorn.org/settings/)
