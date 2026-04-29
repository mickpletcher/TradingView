# TradingView Alpaca Project Analysis

Last reviewed: 2026-04-28

## Purpose

This file is the quick-reference analysis for the `tradingview_alpaca` subproject. It is meant to capture the important information needed before making changes, so future work can start here instead of scanning the whole folder first.

## What This Subproject Is

- `tradingview_alpaca` is the broker-execution module in the `TradingView` repo.
- It receives TradingView webhook alerts through a FastAPI service.
- It validates the payload, applies a small set of safety checks, and submits market orders to Alpaca.
- It is currently designed as an early MVP for local or small-scale use, with paper trading on by default.

## Current Scope

The current implementation supports:

- a `/webhook` endpoint for TradingView alerts
- a `/health` endpoint for liveness checks
- webhook-secret validation through `X-Webhook-Secret`
- payload validation with Pydantic
- Alpaca account, market-open, position, buying-power, quantity, and daily-limit checks
- market order submission through the Alpaca Python SDK
- structured JSON logging
- automated tests around the main success and failure paths

The current implementation does not yet provide:

- durable persistence for safety counters
- a complete container deployment path
- CI automation
- rich order types such as brackets or advanced routing

## Architecture Summary

### Request flow

```text
TradingView alert
  -> FastAPI /webhook
  -> header + payload validation
  -> risk_filter.check_all()
  -> order_manager.build_market_order()
  -> order_manager.submit_order()
  -> structured JSON response
  -> increment in-memory daily counter on success
```

### Module map

- `main.py`
  Owns the FastAPI app, `/webhook`, `/health`, timeout handling, and response construction.

- `config.py`
  Loads settings from environment variables or `.env` using `pydantic-settings`.

- `models.py`
  Defines inbound and outbound models and validates symbol format and maximum quantity.

- `alpaca_client.py`
  Wraps the singleton `TradingClient` and exposes helpers for account, clock, and position lookups.

- `risk_filter.py`
  Applies pre-trade safety checks and stores the current in-memory daily order counter.

- `order_manager.py`
  Builds Alpaca market order requests and submits them through the client wrapper.

- `logger.py`
  Emits structured JSON logs through a custom stdlib logging formatter.

- `tests/test_webhook.py`
  Exercises the HTTP path with mocked Alpaca interactions.

## Runtime And Environment Notes

- The service is meant to run from inside `tradingview_alpaca/`.
- Settings are loaded from a local `.env` file in this folder.
- The repo currently has a virtual environment at the repo root, not inside `tradingview_alpaca/`.
- Local validation that passed on 2026-04-28 used:
  - `..\.venv\Scripts\python.exe -m pytest -q`
- The checked-in docs describe creating `.venv` inside `tradingview_alpaca`, so there is currently a mild docs/runtime mismatch in the working tree.

## Configuration Contract

Expected `.env` fields:

- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`
- `PAPER_TRADING`
- `WEBHOOK_SECRET`
- `MAX_ORDER_QTY`
- `MAX_DAILY_ORDERS`
- `RISK_CHECK_TIMEOUT_SECONDS`
- `ORDER_SUBMIT_TIMEOUT_SECONDS`

Important behavior:

- `PAPER_TRADING=true` is the safe default.
- `WEBHOOK_SECRET` must match the incoming `X-Webhook-Secret` header exactly.
- `MAX_ORDER_QTY` is enforced both at model-validation time and again in `risk_filter.py`.

## Current Behavior Details

### Webhook handling

- Unauthorized requests return HTTP `401`.
- Malformed payloads return HTTP `422`.
- Business-rule failures return HTTP `200` with `status: "skipped"`.
- Runtime failures such as broker exceptions or timeouts return HTTP `200` with `status: "error"`.
- Successful submissions return HTTP `200` with `status: "submitted"`.

### Risk checks currently implemented

- market must be open
- account must not be trading-blocked
- current daily count must be below `MAX_DAILY_ORDERS`
- buying power must be above zero
- quantity must not exceed `MAX_ORDER_QTY`
- duplicate long entries are blocked
- sell requests require an existing position
- sell requests are blocked if the current position is already short

## Strengths

- Clear, small codebase with good separation of concerns.
- FastAPI plus Pydantic gives a simple and readable webhook API.
- Baseline safety controls are already better than a naive “execute every alert” bridge.
- Tests cover the main path plus several important failure paths.
- Logs are structured enough to support later observability improvements.

## Known Risks And Gaps

### 1. Sell-side safety is incomplete

- The sell path checks whether a position exists, but not whether `payload.qty` exceeds the current long size.
- That means a sell intended to close a long could accidentally create a short position on accounts where shorting is permitted.

### 2. Buying power check is too broad

- Buying power is currently checked for both buys and sells.
- A sell-to-close order can be rejected when buying power is zero, even though exiting risk should usually remain allowed.

### 3. Daily order limit is in-memory only

- `_daily_order_count` resets on process restart.
- It also does not coordinate across multiple instances.
- That means it is helpful as an MVP brake but not a durable production control.

### 4. Deployment path is incomplete

- `docker-compose.yml` exists, but there is no Dockerfile in this subproject.
- The compose path also depends on Cloudflare tunnel configuration that is not reflected in `.env.example`.

### 5. Test coverage has gaps around future risk-sensitive work

- Current tests do not cover sell-size validation because that behavior does not exist yet.
- There are also no timeout-specific tests and no persistence-related tests.

### 6. Repo hygiene is a little noisy

- The folder contains tracked Python cache artifacts and local cache directories.
- That makes the working tree noisier than it needs to be and can hide meaningful code changes.

## Validation Status

Validated on 2026-04-28:

- command used: `..\.venv\Scripts\python.exe -m pytest -q`
- working directory: `tradingview_alpaca`
- result: `9 passed`
- warning observed: one deprecation warning from `websockets.legacy`

Test scenarios currently covered:

- valid webhook submission
- wrong secret
- missing symbol
- invalid symbol
- market closed
- health endpoint
- submit-order exception
- daily limit reached
- already long

## File-Level Change Guidance

Before editing, use this as the quick decision guide:

- Change request involves HTTP contract, timeout behavior, or endpoint responses:
  start with `main.py`

- Change request involves settings or startup validation:
  start with `config.py`

- Change request involves payload shape or response schema:
  start with `models.py`

- Change request involves account checks, position logic, daily limits, or trade guardrails:
  start with `risk_filter.py`

- Change request involves order shape or Alpaca submission behavior:
  start with `order_manager.py` and `alpaca_client.py`

- Change request involves observability:
  start with `logger.py`

- Any behavioral change:
  update `tests/test_webhook.py`

## Recommended Next Steps

1. Add sell-size validation so sell orders cannot exceed the current long position unless shorting is explicitly supported.
2. Limit the buying-power check to buy-side flows or redesign it around actual order intent.
3. Move the daily order counter into durable storage.
4. Decide whether Docker deployment is truly supported and either finish it or clearly de-scope it.
5. Add CI to run tests automatically.
6. Clean up tracked cache artifacts so the module is easier to work in.

## Editing Guardrails

When making changes to this subproject:

- preserve paper-trading-first behavior unless the change explicitly targets live-trading support
- treat sell-side logic as the highest-risk area
- keep payload shape changes aligned with other TradingView subprojects where practical
- update this analysis file when major behavior, risks, or entry points change

## Append Log

### 2026-04-28

- Reworked this file from a repo-wide note into an Alpaca-specific quick-reference analysis.
- Confirmed the current test suite passes locally with 9 tests.
- Preserved the core findings: incomplete sell-side safety, overly broad buying-power checks, non-durable daily limits, incomplete containerization, and missing CI.
