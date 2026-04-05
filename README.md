# TradingView to Alpaca Webhook Receiver

FastAPI webhook receiver for TradingView alerts that submits orders to Alpaca after pre trade risk checks.

## Read This First

1. Full app setup and behavior are in [tradingview_alpaca/README.md](tradingview_alpaca/README.md).
2. App code is in [tradingview_alpaca](tradingview_alpaca).
3. Main API entry point is [tradingview_alpaca/main.py](tradingview_alpaca/main.py).

## Quick Navigation

1. Settings model: [tradingview_alpaca/config.py](tradingview_alpaca/config.py)
2. Request and response models: [tradingview_alpaca/models.py](tradingview_alpaca/models.py)
3. Alpaca client wrapper: [tradingview_alpaca/alpaca_client.py](tradingview_alpaca/alpaca_client.py)
4. Order build and submit logic: [tradingview_alpaca/order_manager.py](tradingview_alpaca/order_manager.py)
5. Risk checks: [tradingview_alpaca/risk_filter.py](tradingview_alpaca/risk_filter.py)
6. Structured logging: [tradingview_alpaca/logger.py](tradingview_alpaca/logger.py)
7. Endpoint tests: [tradingview_alpaca/tests/test_webhook.py](tradingview_alpaca/tests/test_webhook.py)

## Service Contract Summary

1. POST /webhook accepts TradingView payloads.
2. Request must include X Webhook Secret header.
3. Response status is submitted, skipped, or error.
4. GET /health returns service state and paper mode.

## Safety Defaults

1. Paper trading is on by default.
2. Live mode requires explicit PAPER_TRADING=false.
3. Quantity and daily order limits are environment controlled.

## Environment Variables

1. ALPACA_API_KEY
2. ALPACA_SECRET_KEY
3. PAPER_TRADING
4. WEBHOOK_SECRET
5. MAX_ORDER_QTY
6. MAX_DAILY_ORDERS
7. RISK_CHECK_TIMEOUT_SECONDS
8. ORDER_SUBMIT_TIMEOUT_SECONDS

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
