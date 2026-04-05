# TradingView → Alpaca Webhook Receiver
# GitHub Copilot Prompt — Full Project Build

## Goal
Build a production-ready FastAPI webhook receiver that accepts TradingView alert
payloads and autonomously executes trades via the Alpaca trading API. Zero human
intervention at execution time. Paper trading by default, switchable to live via
environment variable.

---

## Project structure

tradingview_alpaca/
├── .env.example
├── requirements.txt
├── main.py              # FastAPI app entry point
├── config.py            # Settings via pydantic-settings
├── models.py            # Pydantic request/response models
├── alpaca_client.py     # Alpaca SDK wrapper (singleton)
├── order_manager.py     # Order construction and submission logic
├── risk_filter.py       # Pre-trade risk checks
├── logger.py            # Structured JSON logging
└── tests/
    └── test_webhook.py  # Basic endpoint tests using httpx + pytest

---

## Dependencies — use EXACTLY these, no alternatives

fastapi>=0.111.0
uvicorn[standard]
alpaca-py>=0.26.0        # NOT alpaca-trade-api (legacy, deprecated)
pydantic>=2.0
pydantic-settings>=2.0
python-dotenv
httpx                    # for tests only

---

## Module specs

### config.py
Use pydantic-settings BaseSettings. Load from environment / .env file.
Fields:
- ALPACA_API_KEY: str
- ALPACA_SECRET_KEY: str
- PAPER_TRADING: bool = True         # True = paper, False = live
- WEBHOOK_SECRET: str                # shared secret for request auth
- MAX_ORDER_QTY: int = 100           # hard cap per order
- MAX_DAILY_ORDERS: int = 20         # circuit breaker

### models.py
Pydantic v2 BaseModel for the inbound TradingView webhook payload:
- symbol: str                        # e.g. "AAPL", "SPY"
- side: Literal["buy", "sell"]
- qty: int = Field(gt=0, le=100)
- strategy: str
- price: float | None = None         # {{close}} from TradingView
- interval: str | None = None        # {{interval}} from TradingView
- time: str | None = None            # {{timenow}} from TradingView

Response model:
- status: Literal["submitted", "skipped", "error"]
- order_id: str | None
- symbol: str
- side: str
- qty: int | None
- reason: str | None                 # populated on skipped/error

### alpaca_client.py
Singleton TradingClient from alpaca-py.
- Import TradingClient from alpaca.trading.client
- Instantiate once using config.PAPER_TRADING to set paper= flag
- Expose get_client() function returning the singleton
- Include get_account(), get_clock(), get_open_position(symbol) helpers
  that wrap SDK calls with try/except and raise clean HTTPExceptions

### order_manager.py
Responsible for building and submitting orders. Functions:
- build_market_order(symbol, side, qty) -> MarketOrderRequest
  Use OrderSide enum and TimeInForce.DAY
- build_bracket_order(symbol, side, qty, take_profit_pct, stop_loss_pct)
  Compute limit_price and stop_price from current quote
  Use LimitOrderRequest + TakeProfitRequest + StopLossRequest
- submit_order(order_request) -> Order
  Call client.submit_order(), log the result, return Order object

### risk_filter.py
Run these checks in sequence before any order is submitted.
Return (passed: bool, reason: str).
Checks:
1. Market is open — client.get_clock().is_open
2. Account not blocked — account.trading_blocked == False
3. Buying power sufficient — float(account.buying_power) > 0
4. Order qty does not exceed config.MAX_ORDER_QTY
5. No duplicate position — if side==buy and already long, skip.
   if side==sell and already short or flat with no position, skip.
   Use get_open_position(symbol), handle 404 as no position.
6. Daily order count under config.MAX_DAILY_ORDERS
   Track with a module-level counter that resets at midnight UTC.

### logger.py
Structured JSON logging using Python's stdlib logging + a JSONFormatter.
Each log entry should include:
- timestamp (ISO 8601 UTC)
- level
- event (short slug, e.g. "order_submitted", "risk_check_failed")
- payload dict (symbol, side, qty, strategy, order_id where applicable)

Log every: inbound webhook received, risk check result, order submitted,
order rejected, exception with traceback.

### main.py
FastAPI app. Single POST endpoint at /webhook.
Flow:
1. Validate X-Webhook-Secret header against config.WEBHOOK_SECRET.
   Return 401 if missing or wrong.
2. Parse body into SignalPayload model (FastAPI handles 422 on bad input).
3. Run risk_filter.check_all(payload). If failed, return skipped response.
4. Build MarketOrderRequest via order_manager.build_market_order().
5. Submit via order_manager.submit_order().
6. Return OrderResponse with status="submitted" and order details.
Include a GET /health endpoint returning {"status": "ok", "paper": bool}.

### tests/test_webhook.py
Use pytest + httpx AsyncClient.
Tests:
- POST /webhook with valid payload and correct secret → 200, status=submitted
  Mock alpaca_client so no real API calls are made.
- POST /webhook with wrong secret → 401
- POST /webhook with invalid payload (missing symbol) → 422
- POST /webhook when market is closed → 200, status=skipped
- GET /health → 200

---

## Implementation constraints

- Use alpaca-py SDK exclusively. Never use requests or httpx to call Alpaca
  REST endpoints directly.
- All Alpaca SDK imports from alpaca.trading.* namespace only.
- Paper trading is the default. Live trading requires explicit
  PAPER_TRADING=False in environment — never infer from context.
- No print() statements. All output through logger.py.
- No global mutable state except the singleton client and daily order counter.
- Pydantic v2 syntax throughout (model_validator, not @validator).
- Type hints on every function signature.
- No async Alpaca calls — the SDK is synchronous; wrap in
  asyncio.to_thread() if needed inside async route handlers.

---

## .env.example to generate

ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
PAPER_TRADING=true
WEBHOOK_SECRET=change_me_to_a_long_random_string
MAX_ORDER_QTY=100
MAX_DAILY_ORDERS=20

---

## TradingView alert message body (for reference — do not generate this)

{
  "symbol":   "{{ticker}}",
  "side":     "buy",
  "qty":      10,
  "strategy": "ema_cross",
  "price":    {{close}},
  "interval": "{{interval}}",
  "time":     "{{timenow}}"
}

---

## Start here

Generate all files in the order listed in the project structure.
Begin with config.py and models.py, then alpaca_client.py, then the
remaining modules, then main.py, then tests.
Add a brief docstring to every module explaining its responsibility.