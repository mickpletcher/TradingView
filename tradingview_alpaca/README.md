# TradingView Alpaca Receiver Ops Guide

## Scope

This guide is for day to day run and deploy tasks.
Use the root README for full architecture and webhook details.

## Local Setup

Run from this folder.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit .env and set:

1. ALPACA_API_KEY
2. ALPACA_SECRET_KEY
3. WEBHOOK_SECRET
4. PAPER_TRADING
5. MAX_ORDER_QTY
6. MAX_DAILY_ORDERS
7. RISK_CHECK_TIMEOUT_SECONDS
8. ORDER_SUBMIT_TIMEOUT_SECONDS

## Start API

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Run Tests

```powershell
pytest -q
```

## Send Test Webhook

```powershell
$headers = @{ "X-Webhook-Secret" = "change_me_to_a_long_random_string" }
$body = @{
  symbol = "AAPL"
  side = "buy"
  qty = 10
  strategy = "ema_cross"
  price = 201.34
  interval = "5"
  time = "2026-04-04T14:30:00Z"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/webhook -Headers $headers -Body $body -ContentType "application/json"
```

## Production Run

Use a process manager and disable reload.

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Paper and Live Mode

Paper is default.

Set this for paper:

```env
PAPER_TRADING=true
```

Set this for live:

```env
PAPER_TRADING=false
```

## Common Fixes

401 response:
Secret header does not match WEBHOOK_SECRET.

422 response:
Payload shape is invalid.

Skipped response:
Risk filter blocked order. Check reason in response and logs.

Alpaca call errors:
Confirm key, secret, account status, market state, and network egress.

## Resources

1. [FastAPI docs](https://fastapi.tiangolo.com/)
2. [FastAPI deployment](https://fastapi.tiangolo.com/deployment/)
3. [Pydantic docs](https://docs.pydantic.dev/latest/)
4. [Pydantic settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
5. [Uvicorn settings](https://www.uvicorn.org/settings/)
6. [Alpaca Python SDK](https://alpaca.markets/sdks/python/)
7. [Alpaca Trading API](https://docs.alpaca.markets/reference/trading-api)
8. [Alpaca paper trading](https://docs.alpaca.markets/docs/paper-trading)
9. [TradingView webhooks](https://www.tradingview.com/support/solutions/43000529348-about-webhooks/)
10. [TradingView alerts](https://www.tradingview.com/support/folders/43000560104-alerts/)
11. [HTTPX async docs](https://www.python-httpx.org/async/)
12. [Pytest docs](https://docs.pytest.org/)
