"""Singleton wrapper around the alpaca-py TradingClient with account/position helpers."""

from alpaca.common.exceptions import APIError
from alpaca.trading.client import TradingClient
from alpaca.trading.models import TradeAccount, Clock, Position

from config import settings

_client: TradingClient | None = None


def get_client() -> TradingClient:
    global _client
    if _client is None:
        _client = TradingClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            paper=settings.PAPER_TRADING,
        )
    return _client


def get_account() -> TradeAccount:
    try:
        return get_client().get_account()
    except Exception as exc:
        raise RuntimeError(f"Alpaca get_account failed: {exc}") from exc


def get_clock() -> Clock:
    try:
        return get_client().get_clock()
    except Exception as exc:
        raise RuntimeError(f"Alpaca get_clock failed: {exc}") from exc


def get_open_position(symbol: str) -> Position | None:
    try:
        return get_client().get_open_position(symbol)
    except APIError as exc:
        if exc.status_code == 404:
            return None
        raise RuntimeError(f"Alpaca get_open_position failed: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Alpaca get_open_position failed: {exc}") from exc
