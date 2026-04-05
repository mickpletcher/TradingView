"""Async endpoint tests using httpx + pytest with mocked Alpaca client."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

import os
os.environ.setdefault("ALPACA_API_KEY", "test_key")
os.environ.setdefault("ALPACA_SECRET_KEY", "test_secret")
os.environ.setdefault("WEBHOOK_SECRET", "test_secret_value")

from main import app

VALID_HEADERS = {"X-Webhook-Secret": "test_secret_value"}
VALID_PAYLOAD = {
    "symbol": "AAPL",
    "side": "buy",
    "qty": 10,
    "strategy": "ema_cross",
}


def _make_mock_order() -> MagicMock:
    order = MagicMock()
    order.id = uuid4()
    order.symbol = "AAPL"
    order.side = "buy"
    order.qty = 10
    order.status = "accepted"
    return order


def _open_market_account_mocks() -> tuple[MagicMock, MagicMock, None]:
    clock = MagicMock()
    clock.is_open = True
    account = MagicMock()
    account.trading_blocked = False
    account.buying_power = "10000.00"
    return clock, account, None


@pytest.mark.anyio
async def test_valid_webhook_submitted() -> None:
    clock, account, position = _open_market_account_mocks()
    mock_order = _make_mock_order()

    with (
        patch("alpaca_client.get_clock", return_value=clock),
        patch("alpaca_client.get_account", return_value=account),
        patch("alpaca_client.get_open_position", return_value=position),
        patch("order_manager.submit_order", return_value=mock_order),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/webhook", json=VALID_PAYLOAD, headers=VALID_HEADERS)

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "submitted"
    assert body["symbol"] == "AAPL"


@pytest.mark.anyio
async def test_wrong_secret_returns_401() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json=VALID_PAYLOAD, headers={"X-Webhook-Secret": "wrong"})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_missing_symbol_returns_422() -> None:
    bad_payload = {"side": "buy", "qty": 10, "strategy": "test"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json=bad_payload, headers=VALID_HEADERS)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_invalid_symbol_returns_422() -> None:
    bad_payload = {"symbol": "AAPL$", "side": "buy", "qty": 10, "strategy": "test"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json=bad_payload, headers=VALID_HEADERS)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_market_closed_returns_skipped() -> None:
    clock = MagicMock()
    clock.is_open = False

    with patch("alpaca_client.get_clock", return_value=clock):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/webhook", json=VALID_PAYLOAD, headers=VALID_HEADERS)

    assert resp.status_code == 200
    assert resp.json()["status"] == "skipped"
    assert "closed" in resp.json()["reason"]


@pytest.mark.anyio
async def test_health_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert "paper" in resp.json()


@pytest.mark.anyio
async def test_submit_order_exception_returns_error() -> None:
    clock, account, position = _open_market_account_mocks()

    with (
        patch("alpaca_client.get_clock", return_value=clock),
        patch("alpaca_client.get_account", return_value=account),
        patch("alpaca_client.get_open_position", return_value=position),
        patch("order_manager.submit_order", side_effect=RuntimeError("broker unavailable")),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/webhook", json=VALID_PAYLOAD, headers=VALID_HEADERS)

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "error"
    assert "broker unavailable" in body["reason"]


@pytest.mark.anyio
async def test_daily_limit_reached_returns_skipped() -> None:
    import risk_filter
    clock, account, position = _open_market_account_mocks()

    original_count = risk_filter._daily_order_count
    risk_filter._daily_order_count = risk_filter.settings.MAX_DAILY_ORDERS

    try:
        with (
            patch("alpaca_client.get_clock", return_value=clock),
            patch("alpaca_client.get_account", return_value=account),
            patch("alpaca_client.get_open_position", return_value=position),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/webhook", json=VALID_PAYLOAD, headers=VALID_HEADERS)
    finally:
        risk_filter._daily_order_count = original_count

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "skipped"
    assert "daily order limit" in body["reason"]


@pytest.mark.anyio
async def test_already_long_returns_skipped() -> None:
    from unittest.mock import MagicMock
    clock, account, _ = _open_market_account_mocks()
    existing_position = MagicMock()
    existing_position.qty = "5"

    with (
        patch("alpaca_client.get_clock", return_value=clock),
        patch("alpaca_client.get_account", return_value=account),
        patch("alpaca_client.get_open_position", return_value=existing_position),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/webhook", json=VALID_PAYLOAD, headers=VALID_HEADERS)

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "skipped"
    assert "already long" in body["reason"]
